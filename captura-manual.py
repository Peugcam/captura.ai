"""
Naruto Online Combat Analyzer - Captura Manual
==============================================
Pressione ENTER para iniciar
Pressione CTRL+C para parar
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import ImageGrab, Image
import io

GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 2
QUALITY = 60
RESIZE_TO = (1920, 1080)


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
    print("="*70)
    print("  Naruto Online Combat Analyzer - Captura Manual")
    print("="*70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print()
    print("INSTRUÇÕES:")
    print("  1. Entre em combate no Naruto Online")
    print("  2. Pressione ENTER para INICIAR a captura")
    print("  3. Pressione CTRL+C para PARAR")
    print()

    input("Pressione ENTER quando estiver pronto para iniciar...")
    print()
    print("🎬 CAPTURA INICIADA! Pressione CTRL+C para parar")
    print()

    frame_count = 0
    start_time = time.time()

    try:
        print("[+] Conectando ao WebSocket Gateway...")
        async with websockets.connect(GATEWAY_WS) as websocket:
            print("[OK] Conectado!")

            await websocket.send(json.dumps({"type": "start_capture"}))
            response = await websocket.recv()
            print(f"[<-] {response}")
            print()

            print("[+] Capturando... (CTRL+C para parar)")
            print()

            while True:
                frame_start = time.time()
                frame_data = capture_screen_as_base64()

                if frame_data:
                    frame_msg = {
                        "type": "frame",
                        "data": frame_data,
                        "timestamp": int(time.time() * 1000)
                    }
                    await websocket.send(json.dumps(frame_msg))
                    frame_count += 1

                    elapsed = time.time() - start_time

                    if frame_count % 10 == 0:
                        print(f"[{frame_count} frames] ⏱️  Tempo: {elapsed:.1f}s | FPS: {frame_count/elapsed:.1f}")

                frame_elapsed = time.time() - frame_start
                sleep_time = max(0, (1.0 / CAPTURE_FPS) - frame_elapsed)
                await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        print()
        print()
        print("⏹️  CAPTURA PARADA pelo usuário")
        print()

    except Exception as e:
        print(f"[ERROR] {e}")
        print()
        print("[!] Certifique-se que o gateway está rodando")
        return 1

    elapsed = time.time() - start_time

    print("="*70)
    print("  ✨ Captura Concluída!")
    print("="*70)
    print()
    print(f"✓ {frame_count} frames capturados")
    print(f"✓ Duração: {elapsed:.1f}s")
    print(f"✓ FPS médio: {frame_count/elapsed:.1f}")
    print()
    print("📊 Verifique os resultados:")
    print("   1. Terminal do backend - logs de detecção")
    print("   2. backend/exports/ - Excel com estatísticas")
    print()

    return 0


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print("Programa encerrado.")
