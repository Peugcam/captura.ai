"""
Naruto Online Combat Analyzer - Auto Start
===========================================
Inicia automaticamente após 5 segundos
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
TEST_DURATION = 30  # 30 segundos


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
    print("  Naruto Online Combat Analyzer")
    print("="*70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Duração: {TEST_DURATION}s")
    print()
    print("⏳ Iniciando captura em 5 segundos...")
    print("   Prepare-se! Entre em combate agora!")
    print()

    # Countdown
    for i in range(5, 0, -1):
        print(f"   {i}...")
        await asyncio.sleep(1)

    print()
    print("🎬 INICIANDO CAPTURA!")
    print()

    max_frames = CAPTURE_FPS * TEST_DURATION

    try:
        print("[+] Conectando ao WebSocket Gateway...")
        async with websockets.connect(GATEWAY_WS) as websocket:
            print("[OK] Conectado!")

            await websocket.send(json.dumps({"type": "start_capture"}))
            response = await websocket.recv()
            print(f"[<-] {response}")
            print()

            print(f"[+] Capturando Naruto Online por {TEST_DURATION}s...")
            print()

            start_time = time.time()
            frame_count = 0

            while frame_count < max_frames:
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
                    remaining = TEST_DURATION - elapsed

                    if frame_count % 10 == 0 or frame_count == max_frames:
                        print(f"[{frame_count}/{max_frames}] ⏱️  Tempo restante: {remaining:.1f}s")

                frame_elapsed = time.time() - frame_start
                sleep_time = max(0, (1.0 / CAPTURE_FPS) - frame_elapsed)
                await asyncio.sleep(sleep_time)

            print()
            print("✅ Captura concluída!")
            print("⏳ Aguardando processamento do backend (15s)...")
            await asyncio.sleep(15)

            await websocket.send(json.dumps({"type": "stop_capture"}))
            print("🛑 Stop capture enviado")

            print()
            print("="*70)
            print("  ✨ Análise Concluída!")
            print("="*70)
            print()
            print(f"✓ {frame_count} frames capturados")
            print(f"✓ Duração: {time.time() - start_time:.1f}s")
            print()
            print("📊 Verifique os resultados:")
            print("   1. Terminal do backend - logs de detecção")
            print("   2. backend/exports/ - Excel com estatísticas")
            print()

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[!] Certifique-se que o gateway está rodando")
        return 1

    return 0


if __name__ == "__main__":
    asyncio.run(main())
