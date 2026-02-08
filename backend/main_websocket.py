"""
GTA Analytics V2 - Backend com WebSocket
==========================================

Backend COMPLETO com:
- Polling HTTP do gateway Go
- OCR pre-filtro em thread pool
- GPT-4o Vision API batch processing
- Team tracking em tempo real
- WebSocket server para enviar eventos ao dashboard
- Excel export

Author: Paulo Eugenio Campos
"""

import asyncio
import httpx
import logging
import time
import json
import os
from typing import List, Dict, Set
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import config
from processor import FrameProcessor

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gerencia conexoes WebSocket com limites de segurança"""

    def __init__(self, max_connections: int = 100):
        self.active_connections: Set[WebSocket] = set()
        self.max_connections = max_connections

    async def connect(self, websocket: WebSocket):
        # Verificar limite de conexões
        if len(self.active_connections) >= self.max_connections:
            logger.warning(f"⚠️  Connection limit reached ({self.max_connections}), rejecting new connection")
            await websocket.close(code=1008, reason="Connection limit reached")
            return False

        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🔌 Cliente conectado. Total: {len(self.active_connections)}")
        return True

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"🔌 Cliente desconectado. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes conectados"""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Erro ao enviar para cliente: {e}")
                disconnected.add(connection)

        # Remove conexoes mortas
        for conn in disconnected:
            self.disconnect(conn)


class FramePoller:
    """Poll frames from Go Gateway"""

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_frames(self) -> List[Dict]:
        """Fetch batch of frames from gateway"""
        try:
            response = await self.client.get(f"{self.gateway_url}/frames")

            if response.status_code == 204:  # No content
                return []

            if response.status_code == 200:
                data = response.json()
                frames = data.get('frames', [])
                if frames:
                    logger.info(f"📥 Fetched {len(frames)} frames from gateway")
                return frames

        except Exception as e:
            logger.error(f"Error fetching frames: {e}")

        return []

    async def start_polling(self, callback, interval: float = 1.0):
        """Start continuous polling"""
        logger.info(f"🔄 Started polling gateway every {interval}s")

        while True:
            frames = await self.fetch_frames()

            if frames:
                await callback(frames)

            await asyncio.sleep(interval)


class GTAAnalyticsBackend:
    """Main backend application with WebSocket support"""

    def __init__(self, connection_manager: ConnectionManager):
        self.poller = FramePoller(config.GATEWAY_URL)
        self.processor = FrameProcessor()
        self.frame_buffer = []
        self.last_batch_time = time.time()
        self.last_kill_detection_time = None  # Timestamp da última kill detectada
        self.kill_cooldown = 2.0  # Segundos para esperar após última kill
        self.connection_manager = connection_manager

        logger.info("✅ Frame Processor initialized")
        logger.info(f"   OCR Enabled: {config.OCR_ENABLED}")
        logger.info(f"   OCR Workers: {config.OCR_WORKERS}")
        logger.info(f"   Vision Model: {config.VISION_MODEL}")
        logger.info(f"   Quick Batch: {config.BATCH_SIZE_QUICK} frames / {config.QUICK_BATCH_INTERVAL}s")
        logger.info(f"   Deep Batch: {config.BATCH_SIZE_DEEP} frames / {config.DEEP_BATCH_INTERVAL}s")
        logger.info(f"   Kill Cooldown: {self.kill_cooldown}s (espera após última kill)")

    async def process_frames(self, frames: List[Dict]):
        """Process batch of frames"""
        kills_detected_now = False

        for frame in frames:
            # OCR pre-filtro
            frame_data = await self.processor.process_frame(frame)

            if frame_data:
                self.frame_buffer.append(frame_data)
                kills_detected_now = True

        # Se detectou kills nesse batch, atualiza timestamp
        if kills_detected_now:
            self.last_kill_detection_time = time.time()
            logger.info(f"🔍 Kill detected! Buffer: {len(self.frame_buffer)} frames, waiting for cooldown...")

        # Check se deve processar batch
        await self.check_batch_processing()

    async def check_batch_processing(self):
        """
        Verifica se deve processar batch com lógica de cooldown inteligente

        Estratégia:
        - Se tem frames no buffer E passou o cooldown desde última kill → PROCESSA
        - Se tem muitos frames (>10) → PROCESSA imediatamente (segurança)
        - Caso contrário → ESPERA mais kills
        """
        if not self.frame_buffer:
            return

        current_time = time.time()

        # Se tem muitos frames acumulados (>10), processa imediatamente
        if len(self.frame_buffer) >= 10:
            logger.info(f"⚡ Buffer cheio ({len(self.frame_buffer)} frames), processando tudo!")
            await self.process_batch(len(self.frame_buffer))
            return

        # Se detectou kills recentemente
        if self.last_kill_detection_time:
            time_since_last_kill = current_time - self.last_kill_detection_time

            # Se passou o cooldown E tem pelo menos 1 frame → PROCESSA
            if time_since_last_kill >= self.kill_cooldown and len(self.frame_buffer) >= 1:
                logger.info(f"⏰ Cooldown finished ({time_since_last_kill:.1f}s), processing {len(self.frame_buffer)} frames!")
                await self.process_batch(len(self.frame_buffer))
                self.last_kill_detection_time = None  # Reset
                return

        # Fallback: se passou muito tempo (60s) e tem frames, processa
        elapsed_since_last_batch = current_time - self.last_batch_time
        if elapsed_since_last_batch >= config.DEEP_BATCH_INTERVAL and len(self.frame_buffer) >= 1:
            logger.info(f"⏳ Timeout ({elapsed_since_last_batch:.0f}s), processing remaining {len(self.frame_buffer)} frames")
            await self.process_batch(len(self.frame_buffer))

    async def process_batch(self, batch_size: int):
        """Processa batch de frames com GPT-4o e envia eventos via WebSocket"""
        if not self.frame_buffer:
            return

        # Pegar batch
        batch = self.frame_buffer[:batch_size]
        self.frame_buffer = self.frame_buffer[batch_size:]

        logger.info(f"🔄 Processing batch of {len(batch)} frames...")

        # Processar com Vision AI
        kills = self.processor.process_batch(batch)

        # Enviar eventos via WebSocket
        if kills:
            logger.info(f"🎯 Detected {len(kills)} kills!")
            for kill in kills:
                logger.info(f"   {kill['killer']} ({kill['killer_team']}) -> {kill['victim']} ({kill['victim_team']})")

                # Broadcast evento via WebSocket
                event_message = {
                    "type": "combat_event",
                    "timestamp": datetime.now().isoformat(),
                    "data": kill
                }
                await self.connection_manager.broadcast(event_message)

        # Enviar stats atualizadas
        stats = self.processor.get_stats()
        stats_message = {
            "type": "stats_update",
            "timestamp": datetime.now().isoformat(),
            "data": stats
        }
        await self.connection_manager.broadcast(stats_message)

        logger.info(f"📊 Stats: {stats['frames_processed']} processed | {stats['kills_detected']} kills | {stats['alive']} alive")

        self.last_batch_time = time.time()

    async def stats_reporter(self):
        """Reporta estatisticas periodicamente"""
        while True:
            await asyncio.sleep(30)  # A cada 30s

            stats = self.processor.get_stats()
            logger.info("="*60)
            logger.info("📊 STATISTICS REPORT")
            logger.info("="*60)
            logger.info(f"Frames Received: {stats['frames_received']}")
            logger.info(f"Frames Filtered (OCR): {stats['frames_filtered']} ({stats['filter_efficiency']})")
            logger.info(f"Frames Processed (AI): {stats['frames_processed']}")
            logger.info(f"Kills Detected: {stats['kills_detected']}")
            logger.info(f"Teams: {stats['teams']} | Players: {stats['players']}")
            logger.info(f"Alive: {stats['alive']} | Dead: {stats['dead']}")
            logger.info("="*60)

    async def run_poller(self):
        """Run frame polling"""
        await self.poller.start_polling(self.process_frames, config.POLL_INTERVAL)


# FastAPI app
app = FastAPI(title="GTA Analytics Backend")

# CORS configurado de forma mais segura
# Em produção, substitua ["*"] pela lista de origens permitidas
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if "*" in ALLOWED_ORIGINS:
    logger.warning("⚠️  CORS configurado para aceitar todas as origens (*). "
                  "Em produção, defina ALLOWED_ORIGINS no .env com domínios específicos.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Apenas métodos necessários
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests por 1 hora
)

# Connection manager global
manager = ConnectionManager()

# Backend global
backend = None


@app.on_event("startup")
async def startup_event():
    """Inicializa backend ao iniciar FastAPI"""
    global backend
    backend = GTAAnalyticsBackend(manager)

    logger.info("="*60)
    logger.info("🚀 Starting GTA Analytics Backend V2 - WebSocket Edition")
    logger.info("="*60)
    logger.info(f"📡 Gateway: {config.GATEWAY_URL}")
    logger.info(f"⚙️  OCR Workers: {config.OCR_WORKERS}")
    logger.info(f"🤖 Vision Model: {config.VISION_MODEL}")
    logger.info(f"💾 Export Dir: {config.EXPORT_DIR}")
    logger.info(f"🎮 Game Type: {config.GAME_TYPE}")
    logger.info("="*60)

    # Start background tasks
    asyncio.create_task(backend.stats_reporter())
    asyncio.create_task(backend.run_poller())


@app.get("/")
async def root():
    """Health check"""
    return {"status": "online", "service": "GTA Analytics Backend"}


@app.get("/stats")
async def get_stats():
    """Retorna estatisticas atuais"""
    if backend:
        return backend.processor.get_stats()
    return {"error": "Backend not initialized"}


@app.post("/export")
async def export_to_excel(format: str = "luis"):
    """
    Exporta dados atuais para Excel

    Args:
        format: "luis" (padrão), "standard" ou "advanced"

    Returns:
        Caminho do arquivo gerado
    """
    if not backend:
        raise HTTPException(status_code=503, detail="Backend not initialized")

    # Validar formato
    valid_formats = ["luis", "standard", "advanced"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
        )

    try:
        # Gerar nome do arquivo com timestamp seguro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitizar: remover caracteres perigosos
        safe_format = "".join(c for c in format if c.isalnum())
        filename = f"gta_match_{timestamp}_{safe_format}.xlsx"

        # Criar diretório se não existir com permissões seguras
        os.makedirs(config.EXPORT_DIR, exist_ok=True)

        # Path absoluto para prevenir path traversal
        export_dir_abs = os.path.abspath(config.EXPORT_DIR)
        filepath_abs = os.path.abspath(os.path.join(export_dir_abs, filename))

        # Verificar que o arquivo está dentro do diretório permitido
        if not filepath_abs.startswith(export_dir_abs):
            logger.error(f"⚠️  Path traversal attempt detected: {filepath_abs}")
            raise HTTPException(status_code=400, detail="Invalid file path")

        # Exportar
        backend.processor.export_to_excel(filepath_abs)

        logger.info(f"📊 Excel exportado: {filepath_abs}")

        return {
            "success": True,
            "filename": filename,
            "format": format,
            "size_bytes": os.path.getsize(filepath_abs)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/reset")
async def reset_stats():
    """
    Reseta estatísticas do backend (limpa todos os dados)
    """
    if not backend:
        return {"error": "Backend not initialized"}

    try:
        # Recriar processor (limpa todos os dados)
        backend.processor = FrameProcessor()
        backend.frame_buffer = []

        logger.info("🔄 Backend stats reset!")

        return {"success": True, "message": "Stats reset successfully"}

    except Exception as e:
        logger.error(f"Erro ao resetar: {e}")
        return {"error": str(e)}


@app.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint para enviar eventos em tempo real"""
    connected = await manager.connect(websocket)

    if not connected:
        return  # Conexão rejeitada por limite

    try:
        # Enviar mensagem de boas-vindas
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to GTA Analytics Backend",
            "game_type": config.GAME_TYPE,
            "version": "2.0.0"
        })

        # Manter conexao aberta com rate limiting simples
        message_count = 0
        last_reset = time.time()

        while True:
            # Receber mensagens do cliente (se houver)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)

                # Rate limiting: máximo 60 mensagens por minuto
                current_time = time.time()
                if current_time - last_reset > 60:
                    message_count = 0
                    last_reset = current_time

                message_count += 1
                if message_count > 60:
                    logger.warning(f"⚠️  Client exceeded rate limit, ignoring message")
                    continue

                # Validar tamanho da mensagem (máximo 1KB)
                if len(data) > 1024:
                    logger.warning(f"⚠️  Client sent oversized message ({len(data)} bytes), ignoring")
                    continue

                logger.debug(f"📨 Received from client: {data[:100]}")

            except asyncio.TimeoutError:
                # Timeout normal, continua esperando
                continue
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error receiving WebSocket message: {e}")
                break

    except WebSocketDisconnect:
        logger.info("Cliente desconectou")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


if __name__ == "__main__":
    # Rodar servidor FastAPI com Uvicorn
    uvicorn.run(
        app,
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        log_level="info"
    )
