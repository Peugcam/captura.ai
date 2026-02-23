"""
Teste Simples - Envia frames do vídeo via HTTP (sem WebRTC)
"""
import cv2
import base64
import requests
import time
from pathlib import Path

# Configurações
VIDEO_PATH = r"C:\Users\paulo\OneDrive\Desktop\Atalhos\gta.mp4"
GATEWAY_URL = "http://localhost:8000"
FPS = 2  # 2 frames por segundo
MAX_FRAMES = 20  # Limitar para teste

def main():
    print("="*60)
    print("  TESTE SIMPLES - ENVIO DE FRAMES")
    print("="*60)
    print()

    # Verificar se vídeo existe
    video_path = Path(VIDEO_PATH)
    if not video_path.exists():
        print(f"ERRO: Video nao encontrado: {VIDEO_PATH}")
        return

    print(f"Video: {video_path.name}")
    print(f"FPS: {FPS}")
    print(f"Max frames: {MAX_FRAMES}")
    print()

    # Testar conexão com Gateway
    try:
        r = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        if r.status_code == 200:
            print("[OK] Gateway conectado!")
        else:
            print(f"[ERRO] Gateway retornou: {r.status_code}")
            return
    except Exception as e:
        print(f"[ERRO] Gateway inacessivel: {e}")
        print("Execute: gateway\\gateway.exe -port=8000")
        return

    print()

    # Abrir vídeo
    print("Abrindo video...")
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print("ERRO: Nao foi possivel abrir o video")
        return

    # Propriedades do vídeo
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Total de frames: {total_frames}")
    print(f"FPS do video: {video_fps:.2f}")
    print()

    # Calcular intervalo de frames
    frame_interval = max(1, int(video_fps / FPS))
    print(f"Processando 1 a cada {frame_interval} frames")
    print()

    # Processar frames
    frame_count = 0
    sent_count = 0

    print("Enviando frames...")
    print("-" * 60)

    try:
        while sent_count < MAX_FRAMES:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Pular frames para atingir FPS desejado
            if frame_count % frame_interval != 0:
                continue

            # Converter para JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue

            # Converter para base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Enviar via HTTP POST para /upload
            try:
                response = requests.post(
                    f"{GATEWAY_URL}/upload",
                    json={"frame": frame_base64},
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )

                if response.status_code == 200:
                    sent_count += 1
                    print(f"[{sent_count}/{MAX_FRAMES}] Frame enviado | Tamanho: {len(frame_base64)/1024:.1f} KB")
                else:
                    print(f"[ERRO] Upload falhou: {response.status_code}")

            except Exception as e:
                print(f"[ERRO] Falha ao enviar: {e}")

            # Delay para respeitar FPS
            time.sleep(1.0 / FPS)

    finally:
        cap.release()

    print("-" * 60)
    print()
    print(f"[OK] {sent_count} frames enviados com sucesso!")
    print()
    print("Aguarde alguns segundos para o backend processar...")
    print("Depois verifique:")
    print("  - Stats: curl http://localhost:3000/stats")
    print("  - Dashboard: dashboard-tournament.html")
    print()

if __name__ == "__main__":
    main()
