"""
Naruto Online Analytics - Detector de Combos e Exotericas
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
    print("[ERRO] Instale: pip install obsws-python requests pillow")
    sys.exit(1)

# Configuracoes OBS
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "ZNx3v4LjLVCgbTrO"  # MUDE PARA SUA SENHA

# Backend
BACKEND_URL = "https://gta-analytics-gateway.fly.dev"

# Configuracoes de captura
CAPTURE_FPS = 2  # Capturar 2 frames por segundo

# REGIAO DE CAPTURA - AJUSTAR CONFORME NECESSARIO
# Onde aparecem os combos/exotericas no Naruto Online?
COMBAT_REGION = {
    "x": 0,        # Lado esquerdo da tela
    "y": 300,      # Centro vertical
    "width": 400,  # Largura da area
    "height": 400  # Altura da area
}

frame_count = 0
errors = 0
combos_detected = 0
exotericas_detected = 0

def print_header():
    """Cabecalho do programa"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("")
    print("   NARUTO ONLINE ANALYTICS")
    print("")
    print("   Detector de Combos e Exotericas")
    print("   v1.0")
    print("")
    print("=" * 70)
    print("")

def crop_combat_region(image):
    """Recorta regiao de combate"""
    if image.mode == 'RGBA':
        rgb_image = Image.new('RGB', image.size, (0, 0, 0))
        rgb_image.paste(image, mask=image.split()[3])
        image = rgb_image
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    left = COMBAT_REGION["x"]
    top = COMBAT_REGION["y"]
    right = left + COMBAT_REGION["width"]
    bottom = top + COMBAT_REGION["height"]

    return image.crop((left, top, right, bottom))

def send_frame(image_data):
    """Envia frame para backend"""
    global errors

    try:
        buffer = io.BytesIO()
        image_data.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        response = requests.post(
            f"{BACKEND_URL}/ws",
            json={
                "type": "naruto_frame",
                "data": img_b64,
                "timestamp": int(time.time() * 1000),
                "region": "combat_log"
            },
            timeout=5
        )

        if response.status_code == 200:
            errors = 0
            return True
        else:
            errors += 1
            return False

    except Exception as e:
        errors += 1
        if errors % 30 == 1:
            print(f"[ERRO] Falha ao enviar: {e}")
        return False

def save_frame_locally(image_data, frame_num):
    """Salva frame localmente para debug"""
    output_dir = "naruto_frames"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{output_dir}/frame_{frame_num:04d}.jpg"
    image_data.save(filename, 'JPEG', quality=95)
    return filename

def update_dashboard_data():
    """Atualiza dados para o dashboard"""
    data = {
        "frames": frame_count,
        "combos": combos_detected,
        "exotericas": exotericas_detected,
        "last_frame": f"naruto_frames/frame_{frame_count:04d}.jpg" if frame_count > 0 else None,
        "last_action": {
            "text": f"Frame #{frame_count} capturado",
            "type": "frame"
        }
    }

    with open("naruto_log.json", "w") as f:
        json.dump(data, f)

def main():
    """Loop principal"""
    global frame_count, combos_detected, exotericas_detected

    print_header()

    print("[*] Configuracao:")
    print(f"    Backend: {BACKEND_URL}")
    print(f"    FPS: {CAPTURE_FPS}")
    print(f"    Regiao: {COMBAT_REGION['width']}x{COMBAT_REGION['height']}")
    print("")

    print("[*] Conectando ao OBS WebSocket...")

    try:
        cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3)
        print(f"[OK] Conectado ao OBS ({OBS_HOST}:{OBS_PORT})")

        current_scene = cl.get_current_program_scene()
        scene_name = current_scene.current_program_scene_name
        print(f"[OK] Cena atual: {scene_name}")

        print("")
        print("=" * 70)
        print("")
        print("   CAPTURA ATIVA - MODO DEBUG")
        print("")
        print("   - Frames sendo salvos em: ./naruto_frames/")
        print("   - Pressione Ctrl+C para parar")
        print("")
        print("=" * 70)
        print("")

        start_time = time.time()
        frame_interval = 1.0 / CAPTURE_FPS
        last_frame_time = 0

        while True:
            current_time = time.time()

            if current_time - last_frame_time >= frame_interval:
                try:
                    # Captura screenshot
                    response = cl.get_source_screenshot(
                        name=scene_name,
                        img_format="png",
                        width=1920,
                        height=1080,
                        quality=-1
                    )

                    img_data = response.image_data
                    if not img_data:
                        continue

                    if ',' in img_data:
                        img_data = img_data.split(',', 1)[1]

                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(io.BytesIO(img_bytes))

                    # Recorta regiao de combate
                    combat_region = crop_combat_region(img)

                    # Salva localmente para voce visualizar
                    saved_file = save_frame_locally(combat_region, frame_count + 1)

                    frame_count += 1

                    # Atualiza dados para dashboard
                    update_dashboard_data()

                    if frame_count % 5 == 0 or frame_count == 1:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        print(f"[{frame_count} frames] {elapsed:.0f}s | {fps:.1f} FPS | Salvo: {saved_file}")

                    last_frame_time = current_time

                except Exception as e:
                    if frame_count % 10 == 0:
                        print(f"[ERRO] Captura falhou: {e}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("")
        print("")
        print("[*] Captura interrompida")

    except Exception as e:
        print("")
        print(f"[ERRO] Nao foi possivel conectar ao OBS: {e}")
        print("")
        print("SOLUCAO:")
        print("  1. Abra o OBS Studio")
        print("  2. Menu: Ferramentas -> Configuracoes do Servidor WebSocket")
        print("  3. Marque: 'Ativar Servidor WebSocket'")
        print("  4. Porta: 4455")
        print("  5. Configure a senha neste arquivo (linha 20)")
        print("")

    finally:
        print("")
        print("=" * 70)
        print("")
        print("   CAPTURA FINALIZADA")
        print("")

        if frame_count > 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print(f"   Total: {frame_count} frames")
            print(f"   Tempo: {elapsed:.0f}s")
            print(f"   Media: {fps:.1f} FPS")
            print(f"   Frames salvos em: ./naruto_frames/")
            print("")

        print("=" * 70)
        print("")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
        input("Pressione Enter para sair...")
