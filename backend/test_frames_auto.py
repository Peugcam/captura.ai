"""
Teste Automatico - Deteccao de Frames OBS
==========================================
Monitora frames por 30 segundos e mostra estatisticas
"""

import asyncio
import httpx
import time
from collections import deque
from datetime import datetime

GATEWAY_URL = "http://localhost:8000"
TEST_DURATION = 30  # segundos


class FrameMonitor:
    def __init__(self):
        self.total_frames = 0
        self.fps_history = deque(maxlen=10)
        self.last_check = time.time()
        self.frames_this_second = 0
        self.start_time = time.time()
        self.samples = []

    def update(self, frame_count):
        self.total_frames += frame_count
        self.frames_this_second += frame_count

        now = time.time()
        if now - self.last_check >= 1.0:
            self.fps_history.append(self.frames_this_second)
            self.samples.append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'fps': self.frames_this_second,
                'total': self.total_frames
            })
            self.frames_this_second = 0
            self.last_check = now

    def get_fps(self):
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)

    def display_summary(self):
        print("\n" + "="*70)
        print("RESUMO DO TESTE")
        print("="*70)
        print(f"Duracao: {TEST_DURATION}s")
        print(f"Total de Frames: {self.total_frames}")
        print(f"FPS Medio: {self.get_fps():.1f}")
        print(f"FPS Maximo: {max(self.fps_history) if self.fps_history else 0}")
        print(f"FPS Minimo: {min(self.fps_history) if self.fps_history else 0}")

        fps = self.get_fps()
        print(f"\nAvaliacao: ", end="")
        if fps >= 25:
            print("EXCELENTE - Sistema detectando frames em tempo real!")
        elif fps >= 15:
            print("BOM - Deteccao funcional")
        elif fps > 0:
            print("BAIXO - Pode haver problemas de configuracao")
        else:
            print("FALHA - Nenhum frame detectado")

        if self.samples:
            print("\nAmostras por segundo:")
            for sample in self.samples[-10:]:
                print(f"  {sample['time']}: {sample['fps']} fps (total: {sample['total']})")

        print("="*70)


async def main():
    print("="*70)
    print("TESTE AUTOMATICO - DETECCAO DE FRAMES OBS")
    print("="*70)

    # Testa gateway
    print("\nTestando gateway...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/health")
            if response.status_code == 200:
                print("OK - Gateway esta rodando")
            else:
                print(f"ERRO - Gateway retornou status {response.status_code}")
                return
    except Exception as e:
        print(f"ERRO - Nao foi possivel conectar ao gateway")
        print(f"       Execute: cd gateway && gateway.exe")
        return

    # Inicia monitoramento
    monitor = FrameMonitor()
    print(f"\nIniciando monitoramento por {TEST_DURATION} segundos...")
    print("(O gateway deve estar recebendo frames do OBS)\n")

    start_time = time.time()
    last_display = start_time

    async with httpx.AsyncClient(timeout=30.0) as client:
        while time.time() - start_time < TEST_DURATION:
            try:
                response = await client.get(f"{GATEWAY_URL}/poll")

                if response.status_code == 200:
                    data = response.json()
                    frames = data.get('frames', [])

                    if frames:
                        monitor.update(len(frames))

                # Display a cada 5 segundos
                now = time.time()
                if now - last_display >= 5.0:
                    elapsed = int(now - start_time)
                    remaining = TEST_DURATION - elapsed
                    print(f"[{elapsed}s] Frames: {monitor.total_frames} | FPS: {monitor.get_fps():.1f} | Restam: {remaining}s")
                    last_display = now

                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"Erro: {e}")
                await asyncio.sleep(1.0)

    # Exibe resumo
    monitor.display_summary()

    # Diagnostico
    if monitor.total_frames == 0:
        print("\nDIAGNOSTICO: Nenhum frame foi detectado")
        print("\nVerifique:")
        print("  1. OBS Studio esta aberto e rodando?")
        print("  2. OBS esta transmitindo OU gravando?")
        print("  3. obs-websocket esta instalado e habilitado?")
        print("  4. Gateway esta configurado para receber do OBS?")
        print("\nConsulte TESTE_OBS.md para instrucoes detalhadas")
    else:
        print(f"\nSUCESSO: Sistema detectou {monitor.total_frames} frames!")
        print("O pipeline OBS -> Gateway esta funcionando corretamente")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
