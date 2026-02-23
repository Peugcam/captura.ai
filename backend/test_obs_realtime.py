"""
Script de Teste OBS - Monitor de Frames em Tempo Real
======================================================

Monitora o processamento de frames do OBS em tempo real.
Mostra estatísticas de:
- Frames recebidos por segundo
- Frames processados
- Latência
- Status do pipeline

Usage:
    python test_obs_realtime.py
"""

import asyncio
import httpx
import time
import os
from collections import deque
from datetime import datetime

# URL do gateway (ajuste se necessário)
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class FrameMonitor:
    """Monitor de frames em tempo real"""

    def __init__(self):
        self.total_frames = 0
        self.processed_frames = 0
        self.fps_history = deque(maxlen=10)  # Últimos 10 segundos
        self.last_check = time.time()
        self.frames_this_second = 0

    def update(self, frames_received: int):
        """Atualiza contadores"""
        self.total_frames += frames_received
        self.frames_this_second += frames_received

        # A cada segundo, calcula FPS
        now = time.time()
        if now - self.last_check >= 1.0:
            self.fps_history.append(self.frames_this_second)
            self.frames_this_second = 0
            self.last_check = now

    def get_fps(self) -> float:
        """Retorna FPS médio"""
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)

    def display_stats(self):
        """Exibe estatísticas"""
        print("\n" + "="*60)
        print(f"⏱️  {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        print(f"📊 Total de Frames Recebidos: {self.total_frames}")
        print(f"🎬 FPS Médio: {self.get_fps():.1f} fps")
        print(f"⚡ Frames/segundo atual: {self.frames_this_second}")
        print("="*60)


async def test_gateway_connection():
    """Testa conexão com o gateway"""
    print("\n🔍 Testando conexão com Go Gateway...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/health")

            if response.status_code == 200:
                print(f"✅ Gateway OK: {GATEWAY_URL}")
                data = response.json()
                print(f"   Status: {data.get('status')}")
                print(f"   Frames em fila: {data.get('queue_size', 0)}")
                return True
            else:
                print(f"❌ Gateway retornou status {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro ao conectar no Gateway: {e}")
        print(f"   Verifique se o gateway está rodando em {GATEWAY_URL}")
        return False


async def test_backend_connection():
    """Testa conexão com o backend"""
    print("\n🔍 Testando conexão com Backend Python...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/health")

            if response.status_code == 200:
                print(f"✅ Backend OK: {BACKEND_URL}")
                return True
            else:
                print(f"❌ Backend retornou status {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Erro ao conectar no Backend: {e}")
        print(f"   Verifique se o backend está rodando em {BACKEND_URL}")
        return False


async def monitor_frames():
    """Monitora frames em tempo real"""
    monitor = FrameMonitor()

    print("\n🚀 Iniciando monitoramento de frames...")
    print("   Pressione Ctrl+C para parar\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                # Polling do gateway para pegar frames
                response = await client.get(f"{GATEWAY_URL}/poll")

                if response.status_code == 200:
                    data = response.json()
                    frames = data.get('frames', [])

                    if frames:
                        monitor.update(len(frames))
                        print(f"📦 Recebidos {len(frames)} frames", end='\r')

                # Exibe stats a cada 2 segundos
                if time.time() - monitor.last_check >= 2.0:
                    monitor.display_stats()

                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\n⏹️  Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
                await asyncio.sleep(1.0)

    # Estatísticas finais
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS FINAIS")
    print("="*60)
    monitor.display_stats()


async def main():
    """Função principal"""
    print("="*60)
    print("🎮 GTA ANALYTICS V2 - MONITOR OBS TEMPO REAL")
    print("="*60)

    # Testa conexões
    gateway_ok = await test_gateway_connection()
    backend_ok = await test_backend_connection()

    if not gateway_ok:
        print("\n⚠️  Gateway não está acessível!")
        print("   1. Certifique-se que o Go Gateway está rodando")
        print("   2. Verifique a porta (padrão: 8080)")
        print("   3. Configure OBS para enviar para http://localhost:8080")
        return

    if not backend_ok:
        print("\n⚠️  Backend não está acessível!")
        print("   Execute: python main_websocket.py")
        return

    print("\n✅ Todas as conexões OK!")
    print("\n📹 Instruções:")
    print("   1. Abra o OBS")
    print("   2. Vá em Ferramentas → WebSocket Server Settings")
    print("   3. Configure para enviar para: ws://localhost:8080")
    print("   4. Inicie a gravação/stream")
    print()

    input("Pressione ENTER quando estiver pronto...")

    # Inicia monitoramento
    await monitor_frames()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando...")
