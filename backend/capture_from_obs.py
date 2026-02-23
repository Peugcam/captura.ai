"""
Captura Frames do OBS via WebSocket
====================================
Conecta ao OBS websocket e captura screenshots
"""

import asyncio
import base64
import httpx
from obswebsocket import obsws, requests
import time

# Configuracoes
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Deixe vazio se nao tiver senha
GATEWAY_URL = "http://localhost:8000/upload"
CAPTURE_INTERVAL = 1  # Captura 1 frame por segundo

frames_sent = 0


async def upload_frame(frame_data):
    """Envia frame para o gateway"""
    global frames_sent

    try:
        # Decodifica base64 para bytes
        img_bytes = base64.b64decode(frame_data)

        # Envia via multipart/form-data
        files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(GATEWAY_URL, files=files)

            if response.status_code == 200:
                frames_sent += 1
                print(f"[{time.strftime('%H:%M:%S')}] Frame {frames_sent} enviado com sucesso")
                return True
            else:
                print(f"Erro ao enviar frame: {response.status_code}")
                return False

    except Exception as e:
        print(f"Erro no upload: {e}")
        return False


def capture_screenshot(ws):
    """Captura screenshot do OBS"""
    try:
        # Solicita screenshot da cena atual
        response = ws.call(requests.GetSourceScreenshot(
            sourceName="",  # Vazio = captura a cena inteira
            imageFormat="jpg",
            width=1920,
            height=1080,
            compressionQuality=80
        ))

        # Extrai dados da imagem
        image_data = response.getImageData()

        # Remove prefixo data:image/jpeg;base64,
        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]

        return image_data

    except Exception as e:
        print(f"Erro ao capturar screenshot: {e}")
        return None


async def main():
    print("="*70)
    print("CAPTURA DE FRAMES DO OBS")
    print("="*70)
    print(f"\nConectando ao OBS em {OBS_HOST}:{OBS_PORT}...")

    try:
        # Conecta ao OBS
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()

        print("OK - Conectado ao OBS!")
        print(f"\nCapturando 1 frame por segundo...")
        print("Pressione Ctrl+C para parar\n")

        while True:
            try:
                # Captura screenshot
                frame_data = capture_screenshot(ws)

                if frame_data:
                    # Envia para o gateway
                    await upload_frame(frame_data)
                else:
                    print("Falha ao capturar frame")

                # Aguarda intervalo
                await asyncio.sleep(CAPTURE_INTERVAL)

            except KeyboardInterrupt:
                break

        ws.disconnect()

        print("\n" + "="*70)
        print("RESUMO")
        print("="*70)
        print(f"Total de frames enviados: {frames_sent}")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\nERRO - Nao foi possivel conectar ao OBS")
        print(f"Erro: {e}")
        print("\nVerifique:")
        print("1. OBS esta rodando?")
        print("2. obs-websocket esta habilitado?")
        print("   - Ferramentas > obs-websocket Settings")
        print("   - Porta: 4455 (padrao)")
        print("3. Senha configurada corretamente?")
        print("\nSe nao tiver o obs-websocket:")
        print("  pip install obs-websocket-py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nEncerrando...\n")
