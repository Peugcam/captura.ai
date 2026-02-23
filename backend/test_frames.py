"""
Teste Pratico OBS - Deteccao de Frames
=======================================
Testa a deteccao de frames do OBS em tempo real
"""

import asyncio
import httpx
import time
import os
from collections import deque
from datetime import datetime

# URLs
GATEWAY_URL = "http://localhost:8000"


class FrameMonitor:
    def __init__(self):
        self.total_frames = 0
        self.fps_history = deque(maxlen=10)
        self.last_check = time.time()
        self.frames_this_second = 0
        self.start_time = time.time()

    def update(self, frame_count):
        self.total_frames += frame_count
        self.frames_this_second += frame_count

        now = time.time()
        if now - self.last_check >= 1.0:
            self.fps_history.append(self.frames_this_second)
            self.frames_this_second = 0
            self.last_check = now

    def get_fps(self):
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)

    def get_uptime(self):
        return int(time.time() - self.start_time)

    def display(self):
        print("\n" + "="*60)
        print(f"Tempo: {datetime.now().strftime('%H:%M:%S')} | Uptime: {self.get_uptime()}s")
        print("="*60)
        print(f"Total de Frames: {self.total_frames}")
        print(f"FPS Medio: {self.get_fps():.1f}")
        print(f"FPS Atual: {self.frames_this_second}")

        fps = self.get_fps()
        if fps >= 25:
            print("Status: EXCELENTE (25+ fps)")
        elif fps >= 15:
            print("Status: BOM (15+ fps)")
        elif fps > 0:
            print("Status: BAIXO")
        else:
            print("Status: SEM FRAMES")
        print("="*60)


async def test_gateway():
    print("\n[1/2] Testando Gateway Go...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/health")

            if response.status_code == 200:
                data = response.json()
                print(f"OK - Gateway rodando em {GATEWAY_URL}")
                print(f"    Status: {data.get('status')}")
                return True
            else:
                print(f"ERRO - Status {response.status_code}")
                return False
    except Exception as e:
        print(f"ERRO - Gateway nao esta rodando")
        print(f"       Execute: cd gateway && gateway.exe")
        return False


async def monitor_frames():
    monitor = FrameMonitor()

    print("\n[2/2] Monitorando frames do OBS...")
    print("      Pressione Ctrl+C para parar\n")

    consecutive_empty = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                response = await client.get(f"{GATEWAY_URL}/poll")

                if response.status_code == 200:
                    data = response.json()
                    frames = data.get('frames', [])

                    if frames:
                        consecutive_empty = 0
                        monitor.update(len(frames))
                        print(f"Recebidos {len(frames)} frames", end='\r')
                    else:
                        consecutive_empty += 1
                        if consecutive_empty == 30:
                            print("\nAVISO: Nenhum frame em 30 tentativas")
                            print("       Verifique se o OBS esta transmitindo/gravando")

                # Stats a cada 3 segundos
                if time.time() - monitor.last_check >= 3.0:
                    monitor.display()

                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\nMonitoramento interrompido\n")
                break
            except Exception as e:
                print(f"\nErro: {e}")
                await asyncio.sleep(1.0)

    # Stats finais
    print("\n" + "="*60)
    print("ESTATISTICAS FINAIS")
    print("="*60)
    monitor.display()

    if monitor.total_frames == 0:
        print("\nNENHUM FRAME DETECTADO!")
        print("\nVerifique:")
        print("1. OBS esta rodando?")
        print("2. OBS esta transmitindo ou gravando?")
        print("3. obs-websocket esta configurado?")
        print("4. Gateway esta recebendo frames?")


async def main():
    print("="*60)
    print("GTA ANALYTICS V2 - TESTE DE FRAMES OBS")
    print("="*60)

    # Testa gateway
    gateway_ok = await test_gateway()
    if not gateway_ok:
        return

    # Testa poll
    print("\nTestando polling...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/poll")
            if response.status_code == 200:
                data = response.json()
                frames = data.get('frames', [])
                print(f"OK - Polling funcionando ({len(frames)} frames na fila)")
    except Exception as e:
        print(f"Erro ao testar polling: {e}")

    print("\n" + "="*60)
    print("INSTRUCOES - CONFIGURACAO DO OBS")
    print("="*60)
    print("\n1. Abra o OBS Studio")
    print("2. Adicione uma fonte de captura")
    print("3. Configure obs-websocket:")
    print("   - Ferramentas > WebSocket Server Settings")
    print("   - Habilite o servidor")
    print("   - Configure conexao com o gateway")
    print("\n4. Inicie gravacao/transmissao no OBS")

    input("\n\nPressione ENTER para iniciar monitoramento...")

    await monitor_frames()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
