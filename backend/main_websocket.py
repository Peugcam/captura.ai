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
import base64
from typing import List, Dict, Set
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import config
from processor import FrameProcessor
from src.security import verify_api_key, global_rate_limiter
from roster_manager import RosterManager
from src.multi_api_client import MultiAPIClient

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic models for request validation
class ManualTeamInput(BaseModel):
    """Model for manual team input"""
    tag: str
    full_name: str = ""
    players: List[str] = []


class ManualRosterInput(BaseModel):
    """Model for manual roster input"""
    teams: List[ManualTeamInput]


class PlayerStatusUpdate(BaseModel):
    """Model for updating player status manually"""
    team_tag: str
    player_name: str
    alive: bool


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

    async def start_polling(self, callback, periodic_check_callback, interval: float = 1.0):
        """Start continuous polling with periodic flush check"""
        logger.info(f"🔄 Started polling gateway every {interval}s")

        while True:
            frames = await self.fetch_frames()

            if frames:
                await callback(frames)

            # CRÍTICO: Verificar flush pendente MESMO quando não há frames novos
            # Isso garante que frames acumulados sejam processados quando captura para
            await periodic_check_callback()

            await asyncio.sleep(interval)


class GTAAnalyticsBackend:
    """Main backend application with WebSocket support"""

    def __init__(self, connection_manager: ConnectionManager, roster_manager=None):
        self.poller = FramePoller(config.GATEWAY_URL)
        self.processor = FrameProcessor(roster_manager, connection_manager)
        self.frame_buffer = []
        self.last_batch_time = time.time()
        self.last_kill_detection_time = None  # Timestamp da última kill detectada
        # BUFFER ADAPTATIVO: Ajusta baseado na situação de combate
        self.kill_cooldown_fast = 0.8  # Kill isolada: processa rápido (0.8s)
        self.kill_cooldown_slow = 2.0  # Sequência de kills: aguarda mais (2s)
        self.max_buffer_size = 4  # Máximo de 4 frames antes de processar
        self.max_wait_timeout = 2.5  # Timeout máximo 2.5s para processar frames pendentes
        self.connection_manager = connection_manager

        logger.info("✅ Frame Processor initialized")
        logger.info(f"   OCR Enabled: {config.OCR_ENABLED}")
        logger.info(f"   OCR Workers: {config.OCR_WORKERS}")
        logger.info(f"   Vision Model: {config.VISION_MODEL}")
        logger.info(f"   Quick Batch: {config.BATCH_SIZE_QUICK} frames / {config.QUICK_BATCH_INTERVAL}s")
        logger.info(f"   Deep Batch: {config.BATCH_SIZE_DEEP} frames / {config.DEEP_BATCH_INTERVAL}s")
        logger.info(f"   Kill Cooldown: {self.kill_cooldown_fast}s (isolada) / {self.kill_cooldown_slow}s (sequência)")
        logger.info(f"   Max Buffer Size: {self.max_buffer_size} frames (processa antes de encher)")
        logger.info(f"   Max Wait Timeout: {self.max_wait_timeout}s (força processamento)")

    async def process_frames(self, frames: List[Dict]):
        """Process batch of frames"""
        for frame in frames:
            # Processa frame com Kill Grouping System
            kills = await self.processor.process_frame(frame)

            # Se retornou kills, enviar via WebSocket
            if kills:
                await self.broadcast_kills(kills)

        # IMPORTANTE: Verificar frames pendentes mesmo quando não chegam frames novos
        # Isso permite o AUTO-FLUSH funcionar corretamente
        await self.check_pending_flush()

    async def check_pending_flush(self):
        """
        Verifica periodicamente se há frames pendentes para flush automático
        Isso garante que quando a captura para, processamos em até 0.5s
        """
        if self.processor.pending_frames:
            # Verificar se deve processar (inclui regra de auto-flush)
            if self.processor._should_process_batch():
                kills = await self.processor.flush_pending_frames()
                if kills:
                    await self.broadcast_kills(kills)

    async def broadcast_kills(self, kills: List[Dict]):
        """Envia kills detectadas via WebSocket para dashboard"""
        for kill in kills:
            event = {
                'type': 'kill',
                'data': kill
            }
            await self.connection_manager.broadcast(event)
            logger.info(f"📢 Broadcasting kill: {kill.get('killer')} -> {kill.get('victim')}")

        # Enviar estatísticas completas após cada batch de kills
        await self.broadcast_stats()

    async def broadcast_stats(self):
        """Envia estatísticas completas via WebSocket"""
        try:
            # Obter estatísticas do TeamTracker
            stats = self.processor.tracker.get_match_summary()

            event = {
                'type': 'stats',
                'data': stats
            }
            await self.connection_manager.broadcast(event)
            logger.debug(f"📊 Broadcasting stats: {stats['total_kills']} kills, {len(stats['teams'])} teams")

        except Exception as e:
            logger.error(f"Erro ao enviar estatísticas: {e}")

    async def broadcast_server_detected(self, server_type: str, confidence: float):
        """Envia notificação de servidor GTA detectado via WebSocket"""
        try:
            event = {
                'type': 'server_detected',
                'data': {
                    'server_type': server_type,
                    'confidence': confidence,
                    'timestamp': time.time()
                }
            }
            await self.connection_manager.broadcast(event)
            logger.info(f"🎮 Broadcasting server detection: {server_type} (confidence: {confidence:.2f})")

        except Exception as e:
            logger.error(f"Erro ao enviar detecção de servidor: {e}")

    async def check_batch_processing(self):
        """
        Verifica se deve processar batch com BUFFER ADAPTATIVO INTELIGENTE

        Estratégia OTIMIZADA baseada no contexto de combate:
        - Kill isolada (1-2 frames): processa rápido em 0.8s
        - Sequência (3+ frames): espera 2s para agrupar tudo
        - Buffer cheio (4 frames): processa imediatamente (segurança)
        """
        if not self.frame_buffer:
            return

        current_time = time.time()
        buffer_size = len(self.frame_buffer)

        # NÍVEL 1: Buffer cheio (4 frames) → PROCESSA IMEDIATAMENTE
        if buffer_size >= self.max_buffer_size:
            logger.info(f"⚡ Buffer cheio ({buffer_size} frames), processando agora!")
            await self.process_batch(buffer_size)
            return

        # NÍVEL 2: Cooldown ADAPTATIVO baseado no tamanho do buffer
        if self.last_kill_detection_time:
            time_since_last_kill = current_time - self.last_kill_detection_time

            # ADAPTATIVO: Kill isolada (1-2 frames) = cooldown rápido (0.8s)
            #              Sequência (3+ frames) = cooldown lento (2.0s)
            cooldown = self.kill_cooldown_fast if buffer_size <= 2 else self.kill_cooldown_slow

            # Se passou o cooldown → PROCESSA
            if time_since_last_kill >= cooldown:
                kill_type = "isolada" if buffer_size <= 2 else "sequência"
                logger.info(f"⏰ Cooldown {kill_type} ok ({time_since_last_kill:.1f}s), processando {buffer_size} frames!")
                await self.process_batch(buffer_size)
                self.last_kill_detection_time = None  # Reset
                return

        # NÍVEL 3: Timeout de segurança (2.5s) → FORÇA processamento
        elapsed_since_last_batch = current_time - self.last_batch_time
        if elapsed_since_last_batch >= self.max_wait_timeout and buffer_size >= 1:
            logger.info(f"⏳ Timeout ({elapsed_since_last_batch:.1f}s), processando {buffer_size} frames restantes")
            await self.process_batch(buffer_size)

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

        # Check if server was detected (for GTA only)
        if hasattr(self.processor, 'vision_processor') and hasattr(self.processor.vision_processor, 'detected_server'):
            vision_proc = self.processor.vision_processor
            if vision_proc.detected_server and vision_proc.server_detection_confidence > 0:
                # Broadcast server detection (only once or when it changes)
                await self.broadcast_server_detected(
                    vision_proc.detected_server,
                    vision_proc.server_detection_confidence
                )

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

    async def periodic_flush_timer(self):
        """
        Timer independente que verifica frames pendentes a cada 0.3s
        CRÍTICO: Garante processamento mesmo quando captura para
        """
        while True:
            await asyncio.sleep(0.3)  # Verificar 3x por segundo
            await self.check_pending_flush()

    async def run_poller(self):
        """Run frame polling with periodic flush check"""
        await self.poller.start_polling(
            self.process_frames,
            self.check_pending_flush,
            config.POLL_INTERVAL
        )


# FastAPI app
app = FastAPI(title="GTA Analytics Backend")

# CORS configurado com origens específicas para segurança
# Lista de origens permitidas (production + desenvolvimento local)
ALLOWED_ORIGINS = [
    "https://gta-analytics-backend.fly.dev",
    "https://gta-analytics-gateway.fly.dev",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
    "null"  # Permite file:// protocol para testes locais
]
logger.info(f"🔒 CORS configurado com origens específicas: {ALLOWED_ORIGINS}")

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

# Roster manager global (initialized on startup)
roster_manager = None


@app.on_event("startup")
async def startup_event():
    """Inicializa backend ao iniciar FastAPI"""
    global backend, roster_manager

    # Initialize roster manager FIRST
    roster_manager = RosterManager(MultiAPIClient(config.API_KEYS))

    # Initialize backend WITH roster_manager
    backend = GTAAnalyticsBackend(manager, roster_manager)

    logger.info("="*60)
    logger.info("🚀 Starting GTA Analytics Backend V2 - WebSocket Edition")
    logger.info("="*60)
    logger.info(f"📡 Gateway: {config.GATEWAY_URL}")
    logger.info(f"⚙️  OCR Workers: {config.OCR_WORKERS}")
    logger.info(f"🤖 Vision Model: {config.VISION_MODEL}")
    logger.info(f"💾 Export Dir: {config.EXPORT_DIR}")
    logger.info(f"🎮 Game Type: {config.GAME_TYPE}")
    logger.info(f"🏆 Tournament Mode: Ready")
    logger.info("="*60)

    # Start background tasks
    asyncio.create_task(backend.stats_reporter())
    asyncio.create_task(backend.run_poller())
    asyncio.create_task(backend.periodic_flush_timer())  # Timer independente para auto-flush


@app.get("/")
async def root():
    """Health check"""
    return {"status": "online", "service": "GTA Analytics Backend"}


@app.get("/health")
async def health():
    """Health check endpoint for Fly.io"""
    return {"status": "ok"}


@app.get("/stats")
async def get_stats():
    """Retorna estatisticas atuais"""
    if backend:
        return backend.processor.get_stats()
    return {"error": "Backend not initialized"}


@app.get("/player")
async def serve_player_dashboard():
    """Serve dashboard minimalista para o jogador"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard-player.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard do jogador não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/viewer")
async def serve_viewer_dashboard():
    """Serve dashboard COMPLETO do estrategista V2 - com edição e gerenciamento total"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard-strategist-v2.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard do estrategista V2 não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/monitor")
async def serve_monitor_dashboard():
    """Serve dashboard de monitoramento em tempo real"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard-monitor.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard de monitoramento não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/strategist")
async def serve_strategist_dashboard():
    """Serve dashboard completo do estrategista V2 - com edição e gerenciamento"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard-strategist-v2.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard do estrategista não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/")
async def serve_main_dashboard():
    """Serve dashboard principal OBS"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard-obs.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard principal não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/obs")
async def serve_obs_dashboard():
    """Serve dashboard OBS - Battle Royale Analytics"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard-obs.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard OBS não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.get("/v2")
async def serve_v2_dashboard():
    """Serve dashboard V2 - Battle Royale Analytics V2"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard-v2.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Dashboard V2 não encontrado")
    return FileResponse(dashboard_path, media_type="text/html")


@app.post("/export")
async def export_to_excel(format: str = "luis", api_key: str = Depends(verify_api_key)):
    """
    Exporta dados atuais para Excel

    PROTECTED ENDPOINT - Requires X-API-Key header

    Args:
        format: "luis" (padrão), "standard" ou "advanced"
        api_key: API key from header (injected by dependency)

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
            "filepath": filepath_abs,
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
        # Recriar processor (limpa todos os dados) WITH roster_manager AND connection_manager
        backend.processor = FrameProcessor(roster_manager, manager)
        backend.frame_buffer = []

        logger.info("🔄 Backend stats reset!")

        return {"success": True, "message": "Stats reset successfully"}

    except Exception as e:
        logger.error(f"Erro ao resetar: {e}")
        return {"error": str(e)}


# ============================================================================
# TOURNAMENT ROSTER ENDPOINTS
# ============================================================================

@app.post("/api/tournament/roster/upload")
async def upload_roster_image(file: UploadFile = File(...)):
    """
    Upload tournament bracket image and extract team roster automatically using AI
    Falls back to manual input if extraction fails

    Returns:
        - Extracted roster data with teams and players
        - Confidence score for extraction quality
    """
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    try:
        # Read image file
        image_data = await file.read()

        # Validate file size (max 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")

        # Convert to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')

        logger.info(f"📸 Processing tournament roster image: {file.filename} ({len(image_data)} bytes)")

        # Extract roster using Vision API
        roster_data = await roster_manager.load_from_image(base64_image)

        teams_count = len(roster_data.get('teams', []))

        if teams_count == 0:
            logger.warning("⚠️  No teams extracted from image - AI extraction failed")
            return {
                "success": False,
                "message": "No teams could be extracted from the image. Please use manual input.",
                "data": roster_data,
                "teams_count": 0,
                "requires_manual_input": True
            }

        # Initialize tournament with extracted roster
        success = roster_manager.initialize_tournament_roster(roster_data)

        if success:
            # Broadcast roster loaded event to connected clients
            await manager.broadcast({
                "type": "roster_loaded",
                "data": {
                    "tournament_name": roster_data.get('tournament_name'),
                    "teams_count": teams_count,
                    "teams": roster_manager.get_all_teams()
                }
            })

            logger.info(f"✅ Tournament roster initialized with {teams_count} teams")

            return {
                "success": True,
                "message": f"Successfully extracted {teams_count} teams from image",
                "data": roster_data,
                "teams_count": teams_count,
                "teams": roster_manager.get_all_teams(),
                "requires_manual_input": False
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize tournament roster")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing roster image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.post("/api/tournament/roster/manual")
async def manual_roster_input(roster_input: ManualRosterInput):
    """
    Manually input tournament roster (fallback when AI extraction fails)

    Body:
        {
            "teams": [
                {"tag": "PPP", "full_name": "Team Name", "players": ["player1", "player2", ...]},
                ...
            ]
        }
    """
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    try:
        # Convert Pydantic models to dicts
        teams_data = [team.dict() for team in roster_input.teams]

        # Validate and load roster
        roster_data = roster_manager.load_from_manual_input(teams_data)

        teams_count = len(roster_data.get('teams', []))

        if teams_count == 0:
            raise HTTPException(status_code=400, detail="No valid teams provided")

        # Initialize tournament
        success = roster_manager.initialize_tournament_roster(roster_data)

        if success:
            # Broadcast roster loaded event
            await manager.broadcast({
                "type": "roster_loaded",
                "data": {
                    "tournament_name": "Manual Input",
                    "teams_count": teams_count,
                    "teams": roster_manager.get_all_teams()
                }
            })

            logger.info(f"✅ Tournament roster initialized manually with {teams_count} teams")

            return {
                "success": True,
                "message": f"Tournament initialized with {teams_count} teams",
                "teams_count": teams_count,
                "teams": roster_manager.get_all_teams()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize tournament roster")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in manual roster input: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/tournament/roster")
async def get_current_roster():
    """Get current tournament roster and team status"""
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    return {
        "tournament_mode": roster_manager.tournament_mode,
        "teams_count": len(roster_manager.teams),
        "teams": roster_manager.get_all_teams()
    }


@app.post("/api/tournament/team/add")
async def add_team_to_roster(team: ManualTeamInput):
    """Add a single team to tournament roster (for corrections)"""
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    success = roster_manager.add_team(
        tag=team.tag,
        full_name=team.full_name,
        players=team.players
    )

    if success:
        # Broadcast update
        await manager.broadcast({
            "type": "team_added",
            "data": {
                "team": team.dict(),
                "teams": roster_manager.get_all_teams()
            }
        })

        return {"success": True, "message": f"Team {team.tag} added successfully"}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to add team {team.tag} (may already exist)")


@app.put("/api/tournament/team/{team_tag}")
async def update_team(team_tag: str, team: ManualTeamInput):
    """Update team information (for manual corrections)"""
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    success = roster_manager.update_team(
        tag=team_tag,
        full_name=team.full_name,
        players=team.players
    )

    if success:
        # Broadcast update
        await manager.broadcast({
            "type": "team_updated",
            "data": {
                "team_tag": team_tag,
                "teams": roster_manager.get_all_teams()
            }
        })

        return {"success": True, "message": f"Team {team_tag} updated successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Team {team_tag} not found")


@app.delete("/api/tournament/team/{team_tag}")
async def remove_team(team_tag: str):
    """Remove team from tournament (for manual corrections)"""
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    success = roster_manager.remove_team(team_tag)

    if success:
        # Broadcast update
        await manager.broadcast({
            "type": "team_removed",
            "data": {
                "team_tag": team_tag,
                "teams": roster_manager.get_all_teams()
            }
        })

        return {"success": True, "message": f"Team {team_tag} removed successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Team {team_tag} not found")


@app.post("/api/tournament/player/status")
async def update_player_status(status: PlayerStatusUpdate):
    """
    Manually update player alive/dead status (for manual corrections during match)

    Body:
        {
            "team_tag": "PPP",
            "player_name": "almeida99",
            "alive": false
        }
    """
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    team = roster_manager.get_team(status.team_tag)
    if not team:
        logger.warning(f"❌ Team not found: '{status.team_tag}' (available: {list(roster_manager.teams.keys())})")
        raise HTTPException(status_code=404, detail=f"Team {status.team_tag} not found")

    if status.player_name not in team.players:
        logger.warning(f"❌ Player not found: '{status.player_name}' in team '{status.team_tag}' (available: {list(team.players.keys())})")
        raise HTTPException(status_code=404, detail=f"Player {status.player_name} not found in team {status.team_tag}")

    # Update player status
    team.players[status.player_name].alive = status.alive

    # Broadcast update
    await manager.broadcast({
        "type": "player_status_updated",
        "data": {
            "team_tag": status.team_tag,
            "player_name": status.player_name,
            "alive": status.alive,
            "alive_count": team.alive_count,
            "teams": roster_manager.get_all_teams()
        }
    })

    action = "revived" if status.alive else "marked as dead"
    logger.info(f"✏️  Manual correction: {status.player_name} ({status.team_tag}) {action}")

    return {
        "success": True,
        "message": f"Player {status.player_name} {action}",
        "alive_count": team.alive_count
    }


@app.post("/api/tournament/match/reset")
async def reset_match():
    """Reset match (all players alive, stats cleared) but keep roster"""
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    roster_manager.reset_match()

    # Broadcast reset event
    await manager.broadcast({
        "type": "match_reset",
        "data": {
            "teams": roster_manager.get_all_teams()
        }
    })

    logger.info("🔄 Match reset - all players alive")

    return {
        "success": True,
        "message": "Match reset successfully",
        "teams": roster_manager.get_all_teams()
    }


@app.post("/api/tournament/roster/clear")
async def clear_tournament_roster():
    """Clear tournament roster completely (exit tournament mode)"""
    if not roster_manager:
        raise HTTPException(status_code=503, detail="Roster manager not initialized")

    roster_manager.clear_roster()

    # Broadcast clear event
    await manager.broadcast({
        "type": "roster_cleared",
        "data": {}
    })

    logger.info("🗑️  Tournament roster cleared")

    return {"success": True, "message": "Tournament roster cleared"}


@app.get("/api/tournament/history/teams")
async def get_team_history():
    """Get all known team tags from history"""
    from team_history import get_history_manager

    history = get_history_manager()
    teams = history.get_all_team_tags()

    return {"teams": teams, "count": len(teams)}


@app.get("/api/tournament/history/team/{team_tag}")
async def get_team_stats(team_tag: str):
    """Get historical stats for a specific team"""
    from team_history import get_history_manager

    history = get_history_manager()
    stats = history.get_team_stats(team_tag)

    if not stats:
        raise HTTPException(status_code=404, detail=f"No history found for team {team_tag}")

    return stats


@app.get("/api/tournament/history/players/{team_tag}")
async def get_known_players(team_tag: str, limit: int = 5):
    """Get known players for a team"""
    from team_history import get_history_manager

    history = get_history_manager()
    players = history.get_known_players(team_tag, limit)

    return {"team_tag": team_tag, "players": players, "count": len(players)}


@app.get("/api/tournament/live/stats")
async def get_live_tournament_stats():
    """Get live tournament statistics with historical comparison"""
    from tournament_tracker import get_tracker

    tracker = get_tracker()
    data = tracker.get_live_dashboard_data()

    return data


@app.post("/api/tournament/finish")
async def finish_tournament(winner_tag: str = None):
    """Finish tournament and save to history"""
    from tournament_tracker import get_tracker

    tracker = get_tracker()
    tracker.finish_tournament(winner_tag)

    return {"success": True, "message": "Tournament finished and saved to history"}


@app.get("/tournament")
async def serve_tournament_dashboard():
    """Serve tournament dashboard - permite editar rosters e gerenciar times"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard-tournament.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="Tournament dashboard not found")
    return FileResponse(dashboard_path, media_type="text/html")


# ============================================================================
# FRAME UPLOAD ENDPOINT (Direct upload from OBS/Browser)
# ============================================================================

@app.post("/api/frames/upload")
async def upload_frame(file: UploadFile = File(...)):
    """
    Upload frame directly from OBS Browser Source

    This endpoint allows OBS to send screenshots directly to the cloud backend
    without needing a local gateway.

    Returns:
        JSON with status
    """
    if not backend:
        raise HTTPException(status_code=503, detail="Backend not initialized")

    try:
        # Read image data
        image_data = await file.read()

        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Add to processor queue (simulating gateway frame)
        frame_data = {
            "timestamp": int(time.time() * 1000),
            "data": image_base64
        }

        # Process frame directly
        await backend.processor.process_frames([frame_data])

        logger.info(f"📸 Frame uploaded directly from client ({len(image_data)} bytes)")

        return {"success": True, "message": "Frame uploaded successfully"}

    except Exception as e:
        logger.error(f"❌ Error processing uploaded frame: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# END TOURNAMENT ENDPOINTS
# ============================================================================


@app.websocket("/capture")
async def capture_endpoint(websocket: WebSocket):
    """WebSocket endpoint para RECEBER frames do browser (modo híbrido com Gateway)"""

    # Rate limiting check (usando IP do cliente)
    client_id = f"{websocket.client.host}:{websocket.client.port}"

    if not global_rate_limiter.is_allowed(client_id):
        await websocket.close(code=1008, reason="Rate limit exceeded")
        logger.warning(f"🔒 Rate limit exceeded for {client_id}")
        return

    await websocket.accept()
    logger.info(f"📹 Browser connected for frame capture from {client_id}")

    frame_count = 0

    try:
        while True:
            # Receber frame do browser
            data = await websocket.receive_json()

            if data.get("type") == "frame":
                frame_count += 1
                frame_data = {
                    "data": data.get("data"),
                    "timestamp": data.get("timestamp", time.time()),
                    "number": frame_count
                }

                logger.info(f"📸 Frame {frame_count} received from browser")

                # Processar frame no backend
                if backend:
                    # Adicionar ao buffer do backend para processamento
                    await backend.process_frames([frame_data])

                    # Enviar ACK de volta
                    await websocket.send_json({
                        "type": "ack",
                        "frame": frame_count,
                        "timestamp": time.time()
                    })
                else:
                    logger.error("❌ Backend not initialized!")

            elif data.get("type") == "start_capture":
                logger.info("▶️  Browser started capture")
                frame_count = 0

            elif data.get("type") == "stop_capture":
                logger.info("⏹️  Browser stopped capture")
                break

    except WebSocketDisconnect:
        logger.info(f"📹 Browser disconnected (processed {frame_count} frames)")
    except Exception as e:
        logger.error(f"❌ Error in capture endpoint: {e}")
    finally:
        logger.info(f"✅ Capture session ended: {frame_count} frames processed")


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

                # Parse and broadcast message to all connected clients
                try:
                    msg_data = json.loads(data)

                    # If it's a kill event, broadcast to all clients
                    if msg_data.get('type') == 'kill':
                        kill_data = msg_data.get('data', {})
                        logger.info(f"💀 Kill event: {kill_data.get('killer')} → {kill_data.get('victim')} ({kill_data.get('kill_type')})")

                        # Broadcast to all connected dashboards
                        await manager.broadcast({
                            "type": "kill",
                            "data": kill_data
                        })

                except json.JSONDecodeError:
                    logger.warning(f"⚠️  Invalid JSON received from client")
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")

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
