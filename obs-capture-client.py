"""
GTA Analytics - Cliente de Captura via OBS WebSocket
Alternativa ao plugin - roda fora do OBS
"""
import sys
import io
import time
import asyncio
import json
import base64
import requests
from obswebsocket import obsws, requests as obs_requests
from PIL import Image

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuracoes
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Se configurou senha no OBS WebSocket

GATEWAY_URL = "http://localhost:8000"  # Alterar para Fly.io em producao
CAPTURE_FPS = 4

# Regiao do kill feed (canto superior direito)
KILL_FEED_REGION = {
    "x": 1400,
    "y": 0,
    "width": 520,
    "height": 400
}

frame_count = 0
start_time = None

print("=" * 70)
print("  GTA Analytics - Cliente de Captura OBS")
print("=" * 70)
print()
print("Este programa captura frames do OBS e envia para o backend.")
print()
print(f"OBS WebSocket: {OBS_HOST}:{OBS_PORT}")
print(f"Gateway: {GATEWAY_URL}")
print(f"FPS: {CAPTURE_FPS}")
print(f"Regiao: Kill Feed ({KILL_FEED_REGION['width']}x{KILL_FEED_REGION['height']})")
print()
print("=" * 70)
print()

def crop_kill_feed(image):
    """Recorta apenas a regiao do kill feed"""
    left = KILL_FEED_REGION["x"]
    top = KILL_FEED_REGION["y"]
    right = left + KILL_FEED_REGION["width"]
    bottom = top + KILL_FEED_REGION["height"]

    return image.crop((left, top, right, bottom))

def send_to_gateway(image_data):
    """Envia frame para o Gateway"""
    try:
        # Converte para JPEG
        buffer = io.BytesIO()
        image_data.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        # Envia
        response = requests.post(
            f"{GATEWAY_URL}/ws",  # Endpoint WebSocket do gateway
            json={
                "type": "frame",
                "data": img_b64,
                "timestamp": int(time.time() * 1000),
                "region": "kill_feed"
            },
            timeout=5
        )

        return response.status_code == 200
    except Exception as e:
        print(f"[ERRO] Falha ao enviar: {e}")
        return False

def capture_loop():
    """Loop principal de captura"""
    global frame_count, start_time

    print("[*] Conectando ao OBS WebSocket...")

    try:
        # Conecta ao OBS
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()

        print("[OK] Conectado ao OBS!")
        print()
        print("[*] Iniciando captura... (Ctrl+C para parar)")
        print()

        start_time = time.time()
        frame_interval = 1.0 / CAPTURE_FPS
        last_frame_time = 0

        while True:
            current_time = time.time()

            # Verifica se e hora de capturar
            if current_time - last_frame_time >= frame_interval:
                try:
                    # Captura screenshot do OBS
                    screenshot = ws.call(obs_requests.GetSourceScreenshot(
                        sourceName="",  # Source vazia = captura saida principal
                        imageFormat="jpg",
                        imageWidth=1920,
                        imageHeight=1080,
                        imageCompressionQuality=85
                    ))

                    # Processa imagem
                    img_data = screenshot.getImageData()

                    # Remove prefixo base64
                    if ',' in img_data:
                        img_data = img_data.split(',', 1)[1]

                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(io.BytesIO(img_bytes))

                    # Recorta kill feed
                    kill_feed = crop_kill_feed(img)

                    # Envia para gateway
                    if send_to_gateway(kill_feed):
                        frame_count += 1

                        if frame_count % 10 == 0:
                            elapsed = time.time() - start_time
                            fps = frame_count / elapsed
                            print(f"[{frame_count} frames] {elapsed:.1f}s ({fps:.1f} FPS)")

                    last_frame_time = current_time

                except Exception as e:
                    print(f"[ERRO] Falha ao capturar frame: {e}")

            # Pequena pausa para nao sobrecarregar
            time.sleep(0.05)

    except KeyboardInterrupt:
        print()
        print("[*] Captura interrompida pelo usuario")

    except ConnectionRefusedError:
        print()
        print("[ERRO] Nao foi possivel conectar ao OBS WebSocket!")
        print()
        print("Solucao:")
        print("  1. Abra o OBS Studio")
        print("  2. Ferramentas -> Configuracoes do Servidor WebSocket")
        print("  3. Marque: Ativar Servidor WebSocket")
        print("  4. Porta: 4455")
        print("  5. Aplicar")
        print()

    except Exception as e:
        print()
        print(f"[ERRO] {e}")

    finally:
        try:
            ws.disconnect()
        except:
            pass

        print()
        print("=" * 70)
        print("  Captura Finalizada")
        print("=" * 70)

        if frame_count > 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print()
            print(f"Total: {frame_count} frames em {elapsed:.1f}s ({fps:.1f} FPS)")
            print()

if __name__ == "__main__":
    capture_loop()
