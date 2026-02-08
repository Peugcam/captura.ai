"""
Naruto Online Combat Analyzer - Test Script
============================================
Captura tela do Naruto Online e detecta eventos de combate
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import ImageGrab, Image
import io

GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 2  # 2 FPS para capturar mais ações
QUALITY = 60
RESIZE_TO = (1920, 1080)
TEST_DURATION = 30  # 30 segundos de teste


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
    print("  Naruto Online Combat Analyzer - Test")
    print("="*70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Duração: {TEST_DURATION}s")
    print()
    print("INSTRUÇÕES:")
    print("1. Abra Naruto Online em modo janela")
    print("2. Entre em combate ou batalha")
    print("3. Este script vai capturar por 30 segundos")
    print()

    input("Pressione ENTER quando estiver pronto...")
    print()

    max_frames = CAPTURE_FPS * TEST_DURATION

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
                        print(f"[{frame_count}/{max_frames}] Tempo restante: {remaining:.1f}s")

                # Aguardar próximo frame
                frame_elapsed = time.time() - frame_start
                sleep_time = max(0, (1.0 / CAPTURE_FPS) - frame_elapsed)
                await asyncio.sleep(sleep_time)

            print()
            print("[OK] Captura concluída!")
            print("[i] Aguardando processamento do backend...")
            await asyncio.sleep(15)

            # Stop capture
            await websocket.send(json.dumps({
                "type": "stop_capture"
            }))
            print("[STOP] Stop capture enviado")

            print()
            print("="*70)
            print("  Análise Concluída!")
            print("="*70)
            print()
            print(f"✓ {frame_count} frames capturados")
            print(f"✓ Duração: {time.time() - start_time:.1f}s")
            print()
            print("📊 Verifique os resultados:")
            print("   1. Terminal do backend - logs de detecção")
            print("   2. backend/exports/ - Excel com estatísticas")
            print()
            print("💡 O que o sistema detecta:")
            print("   - Dano causado/recebido")
            print("   - Kills e derrotas")
            print("   - Jutsus e habilidades")
            print("   - Nomes de jogadores")
            print("   - Log de combate")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[!] Certifique-se que o gateway está rodando")
        print("    Execute: start-system.bat")
        return 1

    return 0


if __name__ == "__main__":
    asyncio.run(main())
