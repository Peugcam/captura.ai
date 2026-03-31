"""
GTA Analytics - Cliente de Captura
Versao para Luis - Simples e automatico
"""
import sys
import io
import os
import json
import time
import base64
import requests
from obswebsocket import obsws, requests as obs_requests
from PIL import Image

# Configuracoes
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

# Carregar config
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {
        "gateway_url": "http://localhost:8000",
        "fps": 4,
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

def print_header():
    """Cabecalho do programa"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("")
    print("   GTA ANALYTICS - KILL FEED TRACKER")
    print("")
    print("   Captura Automatica do Kill Feed")
    print("")
    print("=" * 70)
    print("")

def test_gateway():
    """Testa conexao com gateway"""
    print("[*] Testando conexao com Gateway...")
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Gateway online: {GATEWAY_URL}")
            return True
        else:
            print(f"[AVISO] Gateway retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Gateway offline: {e}")
        print("")
        print("SOLUCAO:")
        print("  Verifique se o backend esta rodando")
        print(f"  URL configurada: {GATEWAY_URL}")
        print("")
        return False

def crop_kill_feed(image):
    """Recorta regiao do kill feed com suporte a pixels fixos ou porcentagem"""
    img_w, img_h = image.size

    region = KILL_FEED_REGION

    # Suporte a porcentagem (0.0 a 1.0) ou pixels fixos
    if region.get("percent", False):
        left   = int(region["x"] * img_w)
        top    = int(region["y"] * img_h)
        right  = left + int(region["width"] * img_w)
        bottom = top  + int(region["height"] * img_h)
    else:
        # Pixels fixos: escala proporcional se imagem diferente de 1920x1080
        scale_x = img_w / 1920
        scale_y = img_h / 1080
        left   = int(region["x"] * scale_x)
        top    = int(region["y"] * scale_y)
        right  = left + int(region["width"]  * scale_x)
        bottom = top  + int(region["height"] * scale_y)

    return image.crop((left, top, right, bottom))

def send_frame(image_data):
    """Envia frame para gateway"""
    global errors

    try:
        buffer = io.BytesIO()
        image_data.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

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
            errors = 0  # Reset contador de erros
            return True
        else:
            errors += 1
            return False

    except Exception as e:
        errors += 1
        if errors % 30 == 1:  # Log a cada 30 erros
            print(f"[ERRO] Falha ao enviar: {e}")
        return False

def main():
    """Loop principal"""
    global frame_count

    print_header()

    print("[*] Verificando configuracao...")
    print(f"    Gateway: {GATEWAY_URL}")
    print(f"    FPS: {CAPTURE_FPS}")
    print(f"    Regiao Kill Feed: {KILL_FEED_REGION['width']}x{KILL_FEED_REGION['height']}")
    print("")

    # Testa gateway
    if not test_gateway():
        print("")
        print("[AVISO] Continuando sem gateway (modo offline)")
        print("")

    print("[*] Conectando ao OBS WebSocket...")

    try:
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()

        print(f"[OK] Conectado ao OBS ({OBS_HOST}:{OBS_PORT})")
        print("")
        print("=" * 70)
        print("")
        print("   CAPTURA ATIVA")
        print("")
        print("   - Frames sendo capturados e enviados automaticamente")
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
                    # Captura do OBS (metodo compativel com OBS 28+)
                    screenshot = ws.call(obs_requests.GetSourceScreenshot(
                        sourceName="",
                        imageFormat="png",
                        imageWidth=1920,
                        imageHeight=1080
                    ))

                    # Tenta acessar dados da imagem
                    img_data = screenshot.datain.get('imageData', '')

                    if not img_data:
                        # Fallback para metodo antigo
                        img_data = screenshot.datain.get('img', '')

                    if not img_data:
                        continue

                    if ',' in img_data:
                        img_data = img_data.split(',', 1)[1]

                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(io.BytesIO(img_bytes))

                    # Recorta kill feed
                    kill_feed = crop_kill_feed(img)

                    # Envia
                    if send_frame(kill_feed):
                        frame_count += 1

                        if frame_count % 20 == 0:
                            elapsed = time.time() - start_time
                            fps = frame_count / elapsed
                            print(f"[{frame_count} frames] {elapsed:.0f}s | {fps:.1f} FPS | {errors} erros")

                    last_frame_time = current_time

                except Exception as e:
                    if frame_count % 10 == 0:
                        print(f"[ERRO] Captura falhou: {e}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("")
        print("")
        print("[*] Captura interrompida pelo usuario")

    except ConnectionRefusedError:
        print("")
        print("[ERRO] OBS WebSocket nao esta ativo!")
        print("")
        print("SOLUCAO:")
        print("  1. Abra o OBS Studio")
        print("  2. Menu: Ferramentas -> Configuracoes do Servidor WebSocket")
        print("  3. Marque: 'Ativar Servidor WebSocket'")
        print("  4. Porta: 4455")
        print("  5. Clique em 'Aplicar'")
        print("  6. Execute este programa novamente")
        print("")

    except Exception as e:
        print("")
        print(f"[ERRO] {e}")

    finally:
        try:
            ws.disconnect()
        except:
            pass

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
            print("")

        print("=" * 70)
        print("")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
        input("Pressione Enter para sair...")
