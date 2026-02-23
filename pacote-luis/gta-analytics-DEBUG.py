"""
GTA Analytics V2 - VERSÃO COM DEBUG
"""
import sys
import io
import os
import json
import time
import base64
import requests
from PIL import Image

try:
    import obsws_python as obs
except ImportError:
    print("[ERRO] obsws-python não instalado!")
    sys.exit(1)

# Config
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {
        "gateway_url": "https://gta-analytics-gateway.fly.dev",
        "fps": 1,
        "kill_feed_region": {"x": 1400, "y": 0, "width": 520, "height": 400}
    }

OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "ZNx3v4LjLVCgbTrO"

GATEWAY_URL = config["gateway_url"]
CAPTURE_FPS = config["fps"]
KILL_FEED_REGION = config["kill_feed_region"]

frame_count = 0
errors = 0

def crop_kill_feed(image):
    """Recorta kill feed"""
    if image.mode == 'RGBA':
        rgb_image = Image.new('RGB', image.size, (0, 0, 0))
        rgb_image.paste(image, mask=image.split()[3])
        image = rgb_image
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    left = KILL_FEED_REGION["x"]
    top = KILL_FEED_REGION["y"]
    right = left + KILL_FEED_REGION["width"]
    bottom = top + KILL_FEED_REGION["height"]
    return image.crop((left, top, right, bottom))

def send_frame(image_data):
    """Envia frame"""
    global errors

    try:
        buffer = io.BytesIO()
        image_data.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        print(f"  -> Enviando frame ({len(img_b64)} bytes)...")

        response = requests.post(
            f"{GATEWAY_URL}/ws",
            json={
                "type": "frame",
                "data": img_b64,
                "timestamp": int(time.time() * 1000),
                "region": "kill_feed"
            },
            timeout=5
        )

        if response.status_code == 200:
            print(f"  -> Frame enviado com sucesso!")
            errors = 0
            return True
        else:
            print(f"  -> Erro HTTP {response.status_code}")
            errors += 1
            return False

    except Exception as e:
        print(f"  -> ERRO ao enviar: {e}")
        errors += 1
        return False

def main():
    global frame_count

    print("=" * 70)
    print("   GTA ANALYTICS - DEBUG MODE")
    print("=" * 70)
    print()

    print(f"[*] Gateway: {GATEWAY_URL}")
    print(f"[*] FPS: {CAPTURE_FPS}")
    print()

    try:
        print("[1] Conectando ao OBS...")
        cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3)
        print("[OK] Conectado!")
        print()

        print("[2] Obtendo cena...")
        current_scene = cl.get_current_program_scene()
        scene_name = current_scene.current_program_scene_name
        print(f"[OK] Cena: {scene_name}")
        print()

        print("[3] Iniciando captura...")
        print("    Aguarde, cada captura leva ~2.5 segundos")
        print()

        start_time = time.time()
        frame_interval = 1.0 / CAPTURE_FPS
        last_frame_time = 0

        while True:
            current_time = time.time()

            if current_time - last_frame_time >= frame_interval:
                print(f"\n[Frame #{frame_count + 1}]")
                print(f"  -> Capturando screenshot...")

                try:
                    capture_start = time.time()
                    response = cl.get_source_screenshot(
                        name=scene_name,
                        img_format="png",
                        width=1920,
                        height=1080,
                        quality=-1
                    )
                    capture_time = time.time() - capture_start

                    print(f"  -> Screenshot OK ({capture_time:.2f}s)")

                    img_data = response.image_data
                    if ',' in img_data:
                        img_data = img_data.split(',', 1)[1]

                    print(f"  -> Decodificando imagem...")
                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(io.BytesIO(img_bytes))

                    print(f"  -> Recortando kill feed...")
                    kill_feed = crop_kill_feed(img)

                    if send_frame(kill_feed):
                        frame_count += 1
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        print(f"\n>>> Total: {frame_count} frames | {elapsed:.0f}s | {fps:.2f} FPS | {errors} erros <<<\n")

                    last_frame_time = current_time

                except Exception as e:
                    print(f"  -> ERRO na captura: {e}")
                    import traceback
                    traceback.print_exc()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n[*] Interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n[ERRO] {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print(f"   TOTAL: {frame_count} frames capturados")
    print("=" * 70)

if __name__ == "__main__":
    main()
