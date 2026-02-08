"""
Test Real Video - Processa video GTA real
"""
import asyncio
import websockets
import json
import base64
import os
import subprocess
from pathlib import Path
from PIL import Image
import io

# Configurações
VIDEO_PATH = r"C:\Users\paulo\OneDrive\Desktop\Atalhos\gta.mp4"
FRAMES_DIR = r"C:\Users\paulo\OneDrive\Desktop\gta-analytics-v2\test_frames"
FPS = 1  # 1 frame por segundo
MAX_FRAMES = 20  # Limitar para teste inicial

def extract_frames_from_video():
    """Extrai frames do vídeo usando ffmpeg"""
    print("[+] Extraindo frames do video...")

    # Criar diretório
    Path(FRAMES_DIR).mkdir(exist_ok=True)

    # Limpar frames anteriores
    for f in Path(FRAMES_DIR).glob("*.jpg"):
        f.unlink()

    # Comando ffmpeg: extrai 1 FPS, max 20 frames, qualidade JPEG 50%
    cmd = [
        "ffmpeg",
        "-i", VIDEO_PATH,
        "-vf", f"fps={FPS}",
        "-vframes", str(MAX_FRAMES),
        "-q:v", "10",  # Qualidade JPEG (2=melhor, 31=pior)
        f"{FRAMES_DIR}/frame_%04d.jpg"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Contar frames extraídos
        frames = list(Path(FRAMES_DIR).glob("*.jpg"))
        print(f"[OK] {len(frames)} frames extraidos")
        return len(frames)

    except Exception as e:
        print(f"[ERROR] Erro ao extrair frames: {e}")
        return 0

def load_frame_as_base64(frame_path: str) -> str:
    """Carrega frame e converte para base64"""
    try:
        # Abrir imagem
        img = Image.open(frame_path)

        # Redimensionar para 1920x1080 se necessário (manter aspect ratio)
        if img.size != (1920, 1080):
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

        # Converter para JPEG base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=50)
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"[ERROR] Erro ao carregar frame {frame_path}: {e}")
        return None

async def send_real_frames():
    """Envia frames reais para o gateway"""
    uri = "ws://localhost:8000/ws"

    print("[+] Conectando ao WebSocket Gateway...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Conectado!")

            # Enviar start_capture
            await websocket.send(json.dumps({
                "type": "start_capture"
            }))
            print("[+] Start capture enviado")

            # Aguardar ack
            response = await websocket.recv()
            print(f"[<-] Resposta: {response}")

            # Listar frames extraídos
            frames = sorted(Path(FRAMES_DIR).glob("*.jpg"))
            print(f"\n[+] Processando {len(frames)} frames...")

            # Enviar cada frame
            for i, frame_path in enumerate(frames):
                print(f"\n[{i+1}/{len(frames)}] Processando {frame_path.name}...")

                # Carregar frame
                frame_data = load_frame_as_base64(str(frame_path))

                if not frame_data:
                    print(f"[SKIP] Frame {i+1} pulado")
                    continue

                # Enviar frame
                frame_msg = {
                    "type": "frame",
                    "data": frame_data,
                    "timestamp": int(asyncio.get_event_loop().time() * 1000)
                }

                await websocket.send(json.dumps(frame_msg))
                print(f"[OK] Frame {i+1} enviado ({len(frame_data)} bytes base64)")

                # Delay entre frames (simular captura real)
                await asyncio.sleep(1)

            print("\n[OK] Todos os frames enviados!")
            print("[i] Verifique os logs do backend Python para ver deteccao de kills")
            print("[i] Aguardando processamento em batch...")

            await asyncio.sleep(10)

            # Stop capture
            await websocket.send(json.dumps({
                "type": "stop_capture"
            }))
            print("\n[STOP] Stop capture enviado")

    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        print("\n[!] Certifique-se que o sistema esta rodando:")
        print("   start-system.bat")

if __name__ == "__main__":
    print("="*60)
    print("  GTA Analytics V2 - Test Real Video")
    print("="*60)
    print()
    print(f"Video: {VIDEO_PATH}")
    print(f"FPS: {FPS}")
    print(f"Max Frames: {MAX_FRAMES}")
    print()

    # Verificar se vídeo existe
    if not os.path.exists(VIDEO_PATH):
        print(f"[ERROR] Video nao encontrado: {VIDEO_PATH}")
        exit(1)

    # Extrair frames
    num_frames = extract_frames_from_video()

    if num_frames == 0:
        print("[ERROR] Nenhum frame extraido!")
        exit(1)

    print()

    # Enviar frames
    asyncio.run(send_real_frames())

    print("\n" + "="*60)
    print("  Teste concluido!")
    print("="*60)
    print("\n[i] Verifique backend/exports/ para o Excel com resultados")
