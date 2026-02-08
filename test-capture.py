"""
Test simples de captura - inicia automaticamente
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import ImageGrab, Image
import io

GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 1
QUALITY = 50
RESIZE_TO = (1920, 1080)
MAX_FRAMES = 10  # Apenas 10 frames para teste


def capture_screen_as_base64() -> str:
    """Captura tela e converte para base64"""
    try:
        screenshot = ImageGrab.grab()

        if screenshot.size != RESIZE_TO:
            screenshot = screenshot.resize(RESIZE_TO, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        screenshot.save(buffer, format='JPEG', quality=QUALITY)
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_base64
    except Exception as e:
        print(f"[ERROR] Erro ao capturar tela: {e}")
        return None


async def main():
    """Função principal"""
    print("="*60)
    print("  GTA Analytics V2 - Test Capture (10 frames)")
    print("="*60)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Max Frames: {MAX_FRAMES}")
    print()

    try:
        print("[+] Conectando ao WebSocket Gateway...")
        async with websockets.connect(GATEWAY_WS) as websocket:
            print("[OK] Conectado!")

            # Enviar start_capture
            await websocket.send(json.dumps({
                "type": "start_capture"
            }))

            response = await websocket.recv()
            print(f"[<-] {response}")
            print()

            # Capturar e enviar frames
            print(f"[+] Capturando {MAX_FRAMES} frames da tela...")
            print()

            for i in range(MAX_FRAMES):
                frame_start = time.time()

                frame_data = capture_screen_as_base64()

                if frame_data:
                    frame_msg = {
                        "type": "frame",
                        "data": frame_data,
                        "timestamp": int(time.time() * 1000)
                    }

                    await websocket.send(json.dumps(frame_msg))
                    size_kb = len(frame_data) / 1024
                    print(f"[{i+1}/{MAX_FRAMES}] Frame enviado ({size_kb:.1f} KB)")

                # Aguardar próximo frame
                elapsed = time.time() - frame_start
                sleep_time = max(0, (1.0 / CAPTURE_FPS) - elapsed)
                await asyncio.sleep(sleep_time)

            print()
            print("[OK] Todos os frames enviados!")
            print("[i] Aguardando processamento...")
            await asyncio.sleep(10)

            # Stop capture
            await websocket.send(json.dumps({
                "type": "stop_capture"
            }))
            print("[STOP] Stop capture enviado")

            print()
            print("="*60)
            print("  Teste concluído!")
            print("="*60)
            print()
            print("[i] Verifique:")
            print("   - Terminal do backend para ver processamento")
            print("   - backend/exports/ para Excel")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[!] Certifique-se que o gateway está rodando")
        return 1

    return 0


if __name__ == "__main__":
    asyncio.run(main())
