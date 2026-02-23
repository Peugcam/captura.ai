"""
Captura Tela Diretamente
=========================
Captura a tela e envia frames para o gateway
Mais simples que depender do OBS websocket
"""

import asyncio
import httpx
import time
from PIL import ImageGrab
import io
import base64

GATEWAY_URL = "http://localhost:8000/upload"
CAPTURE_FPS = 2  # 2 frames por segundo
frames_sent = 0


async def capture_and_upload():
    """Captura tela e envia para o gateway"""
    global frames_sent

    try:
        # Captura a tela
        screenshot = ImageGrab.grab()

        # Redimensiona para 1920x1080 se necessario
        if screenshot.size != (1920, 1080):
            screenshot = screenshot.resize((1920, 1080))

        # Converte para JPEG em memoria
        buffer = io.BytesIO()
        screenshot.save(buffer, format='JPEG', quality=80)
        img_bytes = buffer.getvalue()

        # Envia para o gateway
        files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(GATEWAY_URL, files=files)

            if response.status_code == 200:
                frames_sent += 1
                size_kb = len(img_bytes) // 1024
                print(f"[{time.strftime('%H:%M:%S')}] Frame {frames_sent} enviado ({size_kb} KB)")
                return True
            else:
                print(f"Erro: {response.status_code}")
                return False

    except Exception as e:
        print(f"Erro: {e}")
        return False


async def main():
    print("="*70)
    print("CAPTURA DE TELA DIRETA")
    print("="*70)
    print(f"\nCapturando {CAPTURE_FPS} frames/segundo...")
    print("Pressione Ctrl+C para parar\n")

    interval = 1.0 / CAPTURE_FPS

    try:
        while True:
            await capture_and_upload()
            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("RESUMO")
        print("="*70)
        print(f"Total de frames enviados: {frames_sent}")
        print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrando...\n")
