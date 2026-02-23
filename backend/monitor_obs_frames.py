"""
Monitor OBS - Deteccao de Frames em Tempo Real
================================================
Monitora frames vindos do OBS enquanto voce joga
"""

import asyncio
import httpx
import time
from collections import deque
from datetime import datetime

GATEWAY_URL = "http://localhost:8000"
UPDATE_INTERVAL = 2  # segundos


class LiveMonitor:
    def __init__(self):
        self.total_frames = 0
        self.fps_samples = deque(maxlen=30)
        self.last_check = time.time()
        self.frames_this_interval = 0
        self.start_time = time.time()
        self.last_frame_time = None

    def update(self, frame_count):
        now = time.time()
        self.total_frames += frame_count
        self.frames_this_interval += frame_count

        if frame_count > 0:
            self.last_frame_time = now

        # Calcula FPS a cada intervalo
        if now - self.last_check >= 1.0:
            fps = self.frames_this_interval / (now - self.last_check)
            self.fps_samples.append(fps)
            self.frames_this_interval = 0
            self.last_check = now

    def get_avg_fps(self):
        if not self.fps_samples:
            return 0.0
        return sum(self.fps_samples) / len(self.fps_samples)

    def get_current_fps(self):
        if not self.fps_samples:
            return 0.0
        return self.fps_samples[-1] if self.fps_samples else 0.0

    def get_uptime(self):
        return int(time.time() - self.start_time)

    def get_status_emoji(self):
        fps = self.get_avg_fps()
        if fps >= 25:
            return "OTIMO", "green"
        elif fps >= 15:
            return "BOM", "yellow"
        elif fps > 0:
            return "BAIXO", "orange"
        else:
            return "SEM FRAMES", "red"

    def display(self, clear=True):
        if clear:
            # Limpa a tela (funciona no Windows)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')

        status, color = self.get_status_emoji()
        fps_avg = self.get_avg_fps()
        fps_now = self.get_current_fps()

        print("="*70)
        print(f"  MONITOR OBS - NARUTO ONLINE | Tempo: {self.get_uptime()}s")
        print("="*70)
        print(f"\n  Total de Frames: {self.total_frames}")
        print(f"  FPS Medio: {fps_avg:.1f} fps")
        print(f"  FPS Atual: {fps_now:.1f} fps")
        print(f"  Status: {status}")

        if self.last_frame_time:
            seconds_ago = int(time.time() - self.last_frame_time)
            print(f"  Ultimo frame: {seconds_ago}s atras")

        print("\n" + "="*70)

        # Grafico ASCII simples
        if self.fps_samples:
            print("\n  FPS nos ultimos 30 segundos:")
            max_fps = max(self.fps_samples) if self.fps_samples else 1
            for i, fps in enumerate(list(self.fps_samples)[-20:]):
                bar_len = int((fps / max_fps) * 40) if max_fps > 0 else 0
                bar = "#" * bar_len
                print(f"  {bar} {fps:.1f}")

        print("\n  Pressione Ctrl+C para parar")
        print("="*70)


async def monitor():
    monitor = LiveMonitor()

    print("="*70)
    print("  INICIANDO MONITORAMENTO")
    print("="*70)
    print("\n  1. Abra o OBS Studio")
    print("  2. Configure captura do Naruto Online")
    print("  3. INICIE GRAVACAO OU TRANSMISSAO")
    print("  4. Jogue normalmente!")
    print("\n  O sistema detectara os frames automaticamente\n")

    input("  Pressione ENTER quando estiver pronto...")

    consecutive_empty = 0
    last_display = time.time()

    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                # Busca frames
                response = await client.get(f"{GATEWAY_URL}/frames")

                if response.status_code == 200:
                    data = response.json()
                    frames = data.get('frames', [])

                    if frames:
                        consecutive_empty = 0
                        monitor.update(len(frames))
                    else:
                        consecutive_empty += 1

                    # Atualiza display
                    now = time.time()
                    if now - last_display >= UPDATE_INTERVAL:
                        monitor.display(clear=True)
                        last_display = now

                        # Aviso se nao recebeu frames
                        if consecutive_empty >= 10:
                            print("\n  AVISO: Nenhum frame nos ultimos 10s")
                            print("  - OBS esta gravando/transmitindo?")
                            print("  - Fonte de captura configurada?")

                # Pequeno delay
                await asyncio.sleep(0.2)

            except KeyboardInterrupt:
                print("\n\n  Monitoramento encerrado\n")
                break
            except Exception as e:
                print(f"\n  Erro: {e}")
                await asyncio.sleep(2.0)

    # Sumario final
    print("\n" + "="*70)
    print("  SUMARIO FINAL")
    print("="*70)
    print(f"  Duracao: {monitor.get_uptime()}s")
    print(f"  Total de Frames: {monitor.total_frames}")
    print(f"  FPS Medio: {monitor.get_avg_fps():.1f}")
    print("="*70 + "\n")


async def test_connection():
    """Testa conexao com o gateway antes de iniciar"""
    print("\n  Testando conexao com o gateway...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/health")

            if response.status_code == 200:
                print("  OK - Gateway respondendo\n")
                return True
            else:
                print(f"  ERRO - Gateway retornou {response.status_code}\n")
                return False
    except Exception as e:
        print(f"  ERRO - Gateway nao acessivel")
        print(f"  Execute: cd gateway && gateway.exe\n")
        return False


async def main():
    if not await test_connection():
        return

    await monitor()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n  Encerrando...\n")
