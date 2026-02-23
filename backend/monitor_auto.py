"""
Monitor Automatico - Frames OBS em Tempo Real
==============================================
Inicia automaticamente e monitora por 60 segundos
"""

import asyncio
import httpx
import time
from collections import deque
from datetime import datetime

GATEWAY_URL = "http://localhost:8000"
DURATION = 60  # Monitor por 60 segundos


class LiveMonitor:
    def __init__(self):
        self.total_frames = 0
        self.fps_samples = deque(maxlen=30)
        self.last_check = time.time()
        self.frames_this_interval = 0
        self.start_time = time.time()
        self.samples_log = []

    def update(self, frame_count):
        now = time.time()
        self.total_frames += frame_count
        self.frames_this_interval += frame_count

        # Calcula FPS a cada segundo
        if now - self.last_check >= 1.0:
            fps = self.frames_this_interval / (now - self.last_check)
            self.fps_samples.append(fps)
            self.samples_log.append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'fps': fps,
                'total': self.total_frames
            })
            self.frames_this_interval = 0
            self.last_check = now

    def get_avg_fps(self):
        if not self.fps_samples:
            return 0.0
        return sum(self.fps_samples) / len(self.fps_samples)

    def get_uptime(self):
        return int(time.time() - self.start_time)

    def display_summary(self):
        print("\n" + "="*70)
        print("  RESUMO DO MONITORAMENTO")
        print("="*70)
        print(f"  Duracao: {self.get_uptime()}s")
        print(f"  Total de Frames: {self.total_frames}")
        print(f"  FPS Medio: {self.get_avg_fps():.1f}")

        if self.fps_samples:
            print(f"  FPS Maximo: {max(self.fps_samples):.1f}")
            print(f"  FPS Minimo: {min(self.fps_samples):.1f}")

        print("\n  Ultimas 10 amostras:")
        for sample in self.samples_log[-10:]:
            print(f"    {sample['time']}: {sample['fps']:.1f} fps (total: {sample['total']})")

        print("="*70 + "\n")


async def monitor():
    monitor = LiveMonitor()

    print("="*70)
    print("  MONITOR AUTOMATICO - FRAMES OBS")
    print("="*70)
    print(f"\n  Monitorando por {DURATION} segundos...")
    print("  Gateway: {GATEWAY_URL}")
    print("\n  Configure o OBS e inicie gravacao/transmissao!")
    print("  (Pressione Ctrl+C para parar antes)\n")

    start_time = time.time()
    last_display = start_time

    async with httpx.AsyncClient(timeout=10.0) as client:
        while time.time() - start_time < DURATION:
            try:
                # Busca frames
                response = await client.get(f"{GATEWAY_URL}/frames")

                if response.status_code == 200:
                    data = response.json()
                    frames = data.get('frames', [])

                    if frames:
                        monitor.update(len(frames))

                    # Display a cada 5 segundos
                    now = time.time()
                    if now - last_display >= 5.0:
                        elapsed = int(now - start_time)
                        remaining = DURATION - elapsed
                        fps = monitor.get_avg_fps()

                        print(f"  [{elapsed}s] Frames: {monitor.total_frames:4d} | FPS: {fps:5.1f} | Restam: {remaining}s")
                        last_display = now

                await asyncio.sleep(0.2)

            except KeyboardInterrupt:
                print("\n\n  Monitoramento interrompido\n")
                break
            except Exception as e:
                print(f"  Erro: {e}")
                await asyncio.sleep(2.0)

    # Sumario final
    monitor.display_summary()

    # Diagnostico
    if monitor.total_frames == 0:
        print("  DIAGNOSTICO: Nenhum frame foi detectado\n")
        print("  Verifique:")
        print("    1. OBS esta rodando?")
        print("    2. OBS esta GRAVANDO ou TRANSMITINDO?")
        print("    3. Fonte de captura configurada?")
        print("    4. Gateway recebendo frames?\n")
    else:
        print(f"  SUCESSO: {monitor.total_frames} frames detectados!")
        print(f"  Media: {monitor.get_avg_fps():.1f} FPS\n")

        if monitor.get_avg_fps() >= 25:
            print("  Status: EXCELENTE - Pipeline funcionando perfeitamente!")
        elif monitor.get_avg_fps() >= 15:
            print("  Status: BOM - Sistema operacional")
        elif monitor.get_avg_fps() > 0:
            print("  Status: BAIXO - Verifique configuracoes do OBS")

    print()


async def main():
    print("\n  Testando conexao com o gateway...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/health")

            if response.status_code == 200:
                print("  OK - Gateway respondendo\n")
            else:
                print(f"  ERRO - Gateway retornou {response.status_code}\n")
                return
    except Exception as e:
        print(f"  ERRO - Gateway nao acessivel")
        print(f"  Execute: cd gateway && gateway.exe\n")
        return

    await monitor()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n  Encerrando...\n")
