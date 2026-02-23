"""
Teste Prático OBS - Detecção de Frames
=======================================

Script para testar a detecção de frames do OBS em tempo real.
Mostra estatísticas detalhadas sobre:
- Frames recebidos por segundo
- Tamanho dos frames
- Latência do pipeline
- Status de cada componente

Usage:
    python test_frame_detection.py
"""

import asyncio
import httpx
import time
import os
import sys
from collections import deque
from datetime import datetime
from typing import Optional

# URLs dos serviços
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")


class FrameDetectionMonitor:
    """Monitor avançado de detecção de frames"""

    def __init__(self):
        self.total_frames = 0
        self.fps_history = deque(maxlen=10)
        self.size_history = deque(maxlen=100)
        self.last_check = time.time()
        self.frames_this_second = 0
        self.start_time = time.time()
        self.last_frame_time = None
        self.frame_gaps = deque(maxlen=100)

    def update(self, frames: list):
        """Atualiza contadores com novos frames"""
        current_time = time.time()

        if frames:
            self.total_frames += len(frames)
            self.frames_this_second += len(frames)

            # Calcula gap entre frames
            if self.last_frame_time:
                gap = current_time - self.last_frame_time
                self.frame_gaps.append(gap)

            self.last_frame_time = current_time

            # Registra tamanho dos frames
            for frame in frames:
                if isinstance(frame, dict) and 'data' in frame:
                    frame_size = len(frame['data']) if frame['data'] else 0
                    self.size_history.append(frame_size)

        # Atualiza FPS a cada segundo
        if current_time - self.last_check >= 1.0:
            self.fps_history.append(self.frames_this_second)
            self.frames_this_second = 0
            self.last_check = current_time

    def get_fps(self) -> float:
        """Retorna FPS médio"""
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)

    def get_current_fps(self) -> int:
        """Retorna FPS atual"""
        return self.frames_this_second

    def get_avg_frame_size(self) -> int:
        """Retorna tamanho médio de frame em KB"""
        if not self.size_history:
            return 0
        return int(sum(self.size_history) / len(self.size_history) / 1024)

    def get_avg_gap(self) -> float:
        """Retorna gap médio entre frames"""
        if not self.frame_gaps:
            return 0.0
        return sum(self.frame_gaps) / len(self.frame_gaps)

    def get_uptime(self) -> int:
        """Retorna tempo de execução em segundos"""
        return int(time.time() - self.start_time)

    def display_stats(self):
        """Exibe estatísticas detalhadas"""
        print("\n" + "="*70)
        print(f"⏱️  {datetime.now().strftime('%H:%M:%S')} | Uptime: {self.get_uptime()}s")
        print("="*70)
        print(f"📊 Total de Frames: {self.total_frames}")
        print(f"🎬 FPS Médio: {self.get_fps():.1f} fps")
        print(f"⚡ FPS Atual: {self.get_current_fps()} fps")
        print(f"📦 Tamanho Médio: {self.get_avg_frame_size()} KB/frame")
        print(f"⏲️  Gap Médio: {self.get_avg_gap():.3f}s entre frames")

        # Status visual
        fps = self.get_fps()
        if fps >= 25:
            status = "🟢 EXCELENTE"
        elif fps >= 15:
            status = "🟡 BOM"
        elif fps > 0:
            status = "🟠 BAIXO"
        else:
            status = "🔴 SEM FRAMES"

        print(f"Status: {status}")
        print("="*70)


async def test_gateway_health() -> bool:
    """Testa saúde do gateway"""
    print("\n🔍 Testando Gateway Go...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/health")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Gateway OK: {GATEWAY_URL}")
                print(f"   Status: {data.get('status', 'unknown')}")

                queue_size = data.get('queue_size', 0)
                if queue_size > 0:
                    print(f"   📦 Frames na fila: {queue_size}")
                else:
                    print(f"   📭 Fila vazia (esperando frames do OBS)")

                return True
            else:
                print(f"❌ Gateway retornou status {response.status_code}")
                return False

    except httpx.ConnectError:
        print(f"❌ Gateway não está rodando em {GATEWAY_URL}")
        print("   Execute: cd gateway && gateway.exe")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar no Gateway: {e}")
        return False


async def test_backend_health() -> bool:
    """Testa saúde do backend"""
    print("\n🔍 Testando Backend Python...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/health")

            if response.status_code == 200:
                print(f"✅ Backend OK: {BACKEND_URL}")
                return True
            else:
                print(f"❌ Backend retornou status {response.status_code}")
                return False

    except httpx.ConnectError:
        print(f"❌ Backend não está rodando em {BACKEND_URL}")
        print("   Execute: cd backend && python main_websocket.py")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar no Backend: {e}")
        return False


async def test_gateway_poll() -> Optional[dict]:
    """Testa polling do gateway"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/poll")

            if response.status_code == 200:
                return response.json()
            else:
                return None

    except Exception as e:
        print(f"\n❌ Erro ao fazer polling: {e}")
        return None


async def monitor_frame_detection():
    """Monitora detecção de frames em tempo real"""
    monitor = FrameDetectionMonitor()

    print("\n🚀 Iniciando monitoramento de frames...")
    print("   Pressione Ctrl+C para parar\n")

    consecutive_empty = 0
    poll_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                poll_count += 1

                # Polling do gateway
                response = await client.get(f"{GATEWAY_URL}/poll")

                if response.status_code == 200:
                    data = response.json()
                    frames = data.get('frames', [])

                    if frames:
                        consecutive_empty = 0
                        monitor.update(frames)
                        print(f"📦 Recebidos {len(frames)} frames (poll #{poll_count})", end='\r')
                    else:
                        consecutive_empty += 1
                        if consecutive_empty % 10 == 0:
                            print(f"\n⚠️  Nenhum frame recebido nas últimas {consecutive_empty} tentativas")
                            print("   Verifique se o OBS está transmitindo/gravando")

                # Exibe stats a cada 3 segundos
                if time.time() - monitor.last_check >= 3.0:
                    monitor.display_stats()

                # Delay entre polls
                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\n⏹️  Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
                await asyncio.sleep(1.0)

    # Estatísticas finais
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS FINAIS")
    print("="*70)
    monitor.display_stats()

    if monitor.total_frames == 0:
        print("\n⚠️  NENHUM FRAME FOI DETECTADO!")
        print("\nPossíveis causas:")
        print("1. OBS não está rodando")
        print("2. OBS não está transmitindo/gravando")
        print("3. Plugin obs-websocket não está configurado")
        print("4. Gateway não está recebendo frames do OBS")
        print("\nVerifique o arquivo TESTE_OBS.md para instruções completas")


async def main():
    """Função principal"""
    print("="*70)
    print("🎮 GTA ANALYTICS V2 - TESTE DE DETECÇÃO DE FRAMES OBS")
    print("="*70)

    # Testa gateway
    gateway_ok = await test_gateway_health()
    if not gateway_ok:
        print("\n❌ Gateway não está acessível. Abortando teste.")
        print("\nPara iniciar o gateway:")
        print("  cd gateway")
        print("  gateway.exe")
        return

    # Testa backend
    backend_ok = await test_backend_health()
    if not backend_ok:
        print("\n⚠️  Backend não está acessível (opcional para este teste)")

    # Testa uma chamada de poll
    print("\n🔍 Testando polling do gateway...")
    poll_result = await test_gateway_poll()

    if poll_result is not None:
        frames = poll_result.get('frames', [])
        print(f"✅ Polling funcionando ({len(frames)} frames na fila)")
    else:
        print("⚠️  Polling retornou vazio (gateway aguardando frames)")

    print("\n" + "="*70)
    print("📹 INSTRUÇÕES - CONFIGURAÇÃO DO OBS")
    print("="*70)
    print("\n1. Abra o OBS Studio")
    print("2. Adicione uma fonte de captura (jogo, tela, etc)")
    print("3. Configure o obs-websocket:")
    print("   - Ferramentas → WebSocket Server Settings")
    print("   - Habilite o servidor")
    print("   - Porta: 4455 (padrão)")
    print("   - Configure para enviar para o gateway")
    print("\n4. Inicie a gravação ou transmissão no OBS")
    print("\n5. O gateway irá capturar os frames automaticamente")

    input("\n\nPressione ENTER quando estiver pronto para começar o monitoramento...")

    # Inicia monitoramento
    await monitor_frame_detection()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando...")
