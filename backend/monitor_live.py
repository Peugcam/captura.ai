"""
Monitor Live - Deteccao Continua de Frames
===========================================
Monitora continuamente e mostra updates em tempo real
"""

import asyncio
import httpx
import time
from datetime import datetime

GATEWAY_URL = "http://localhost:8000"

total_frames = 0
last_total = 0
start_time = time.time()

async def check_frames():
    global total_frames, last_total

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{GATEWAY_URL}/frames")

            if response.status_code == 200:
                data = response.json()
                frames = data.get('frames', [])

                if frames:
                    total_frames += len(frames)
                    new_frames = total_frames - last_total

                    now = datetime.now().strftime('%H:%M:%S')
                    uptime = int(time.time() - start_time)

                    print(f"[{now}] +{new_frames} frames | Total: {total_frames} | Uptime: {uptime}s")
                    last_total = total_frames

                    return len(frames)
    except Exception as e:
        print(f"Erro: {e}")

    return 0

async def monitor():
    print("="*70)
    print("MONITOR LIVE - AGUARDANDO FRAMES DO OBS")
    print("="*70)
    print("\nINSTRUCOES:")
    print("1. Abra o OBS")
    print("2. Clique em 'Iniciar Gravacao' ou 'Iniciar Transmissao'")
    print("3. Os frames aparecerao automaticamente aqui!\n")
    print("Monitorando... (Ctrl+C para parar)\n")

    consecutive_empty = 0

    while True:
        try:
            frames_received = await check_frames()

            if frames_received == 0:
                consecutive_empty += 1

                # Aviso a cada 30 segundos sem frames
                if consecutive_empty == 30:
                    print(f"\n[AVISO] Nenhum frame em 30s - OBS esta gravando/transmitindo?")
                    consecutive_empty = 0
            else:
                consecutive_empty = 0

            await asyncio.sleep(1)

        except KeyboardInterrupt:
            break

    print("\n" + "="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Total de Frames: {total_frames}")
    print(f"Tempo: {int(time.time() - start_time)}s")

    if total_frames > 0:
        fps = total_frames / (time.time() - start_time)
        print(f"FPS Medio: {fps:.1f}")
        print("\nSUCESSO! Sistema detectando frames do OBS!")
    else:
        print("\nNenhum frame detectado.")
        print("Certifique-se que o OBS esta GRAVANDO ou TRANSMITINDO!")

    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\n\nEncerrando...\n")
