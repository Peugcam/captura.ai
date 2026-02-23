"""
Monitor Fly.dev - Ver frames capturados em tempo real
======================================================
Mostra estatisticas do servidor a cada segundo
"""

import asyncio
import httpx
import time
from datetime import datetime

SERVER_URL = "https://gta-analytics-v2.fly.dev"

async def monitor():
    print("="*70)
    print("MONITOR FLY.DEV - FRAMES EM TEMPO REAL")
    print("="*70)
    print(f"\n[*] Servidor: {SERVER_URL}")
    print("[*] Atualizando a cada 2 segundos...")
    print("[!] Pressione Ctrl+C para parar\n")
    print("="*70 + "\n")

    last_frames = 0
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            while True:
                try:
                    # Buscar stats do servidor
                    response = await client.get(f"{SERVER_URL}/stats")

                    if response.status_code == 200:
                        stats = response.json()

                        frames_received = stats.get('frames_received', 0)
                        frames_processed = stats.get('frames_processed', 0)
                        kills_detected = stats.get('kills_detected', 0)
                        teams = stats.get('teams', 0)
                        players = stats.get('players', 0)
                        alive = stats.get('alive', 0)
                        dead = stats.get('dead', 0)

                        # Calcular novos frames
                        new_frames = frames_received - last_frames
                        last_frames = frames_received

                        # Calcular uptime
                        uptime = int(time.time() - start_time)
                        fps_avg = frames_received / uptime if uptime > 0 else 0

                        # Timestamp
                        now = datetime.now().strftime('%H:%M:%S')

                        # Mostrar stats
                        if new_frames > 0:
                            print(f"[{now}] [+{new_frames}] Total: {frames_received} frames | "
                                  f"Processados: {frames_processed} | "
                                  f"Kills: {kills_detected} | "
                                  f"FPS medio: {fps_avg:.2f}")
                        else:
                            print(f"[{now}] [  ] Total: {frames_received} frames | "
                                  f"Processados: {frames_processed} | "
                                  f"Kills: {kills_detected} | "
                                  f"Times: {teams} | Jogadores: {players} ({alive} vivos)")

                    else:
                        print(f"[ERROR] Servidor retornou: {response.status_code}")

                except httpx.TimeoutException:
                    print("[TIMEOUT] Servidor nao respondeu")
                except Exception as e:
                    print(f"[ERROR] {e}")

                # Aguardar 2 segundos
                await asyncio.sleep(2)

    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("RESUMO FINAL")
        print("="*70)
        print(f"[*] Tempo monitoramento: {uptime}s")
        print(f"[*] Total frames recebidos: {last_frames}")
        print(f"[*] FPS medio: {fps_avg:.2f}")
        print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\n[*] Encerrando...\n")
