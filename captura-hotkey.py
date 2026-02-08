"""
Naruto Online Combat Analyzer - Controle por Teclas
===================================================
F9  = INICIAR captura
F10 = PARAR captura
ESC = SAIR do programa
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import ImageGrab, Image
import io
import keyboard
import threading

GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 4  # Aumentado para capturar combos rápidos melhor
QUALITY = 60
RESIZE_TO = (1920, 1080)

# Controle
capturing = False
should_exit = False
websocket_conn = None
frame_count = 0
start_time = None


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


def on_f9():
    """Callback para F9 - Iniciar"""
    global capturing, frame_count, start_time
    if not capturing:
        capturing = True
        frame_count = 0
        start_time = time.time()
        print()
        print("🎬 CAPTURA INICIADA! (Pressione F10 para parar)")
        print()


def on_f10():
    """Callback para F10 - Parar"""
    global capturing
    if capturing:
        capturing = False
        elapsed = time.time() - start_time
        print()
        print("⏹️  CAPTURA PARADA!")
        print(f"✓ {frame_count} frames capturados em {elapsed:.1f}s")
        print()


def on_esc():
    """Callback para ESC - Sair"""
    global should_exit, capturing
    capturing = False
    should_exit = True
    print()
    print("🚪 Encerrando programa...")


async def capture_loop():
    """Loop de captura"""
    global websocket_conn, frame_count, capturing

    try:
        async with websockets.connect(GATEWAY_WS) as websocket:
            websocket_conn = websocket
            print("[OK] Conectado ao gateway!")
            print()

            await websocket.send(json.dumps({"type": "start_capture"}))

            last_frame_time = 0
            frame_interval = 1.0 / CAPTURE_FPS

            while not should_exit:
                if capturing:
                    current_time = time.time()

                    if current_time - last_frame_time >= frame_interval:
                        frame_data = capture_screen_as_base64()

                        if frame_data:
                            frame_msg = {
                                "type": "frame",
                                "data": frame_data,
                                "timestamp": int(time.time() * 1000)
                            }
                            await websocket.send(json.dumps(frame_msg))
                            frame_count += 1

                            if frame_count % 10 == 0:
                                elapsed = time.time() - start_time
                                print(f"[{frame_count} frames] ⏱️  {elapsed:.1f}s | FPS: {frame_count/elapsed:.1f}")

                            last_frame_time = current_time

                await asyncio.sleep(0.1)

            await websocket.send(json.dumps({"type": "stop_capture"}))

    except Exception as e:
        print(f"[ERROR] {e}")


async def main():
    """Função principal"""
    global should_exit

    print("="*70)
    print("  Naruto Online Combat Analyzer - Controle por Teclas")
    print("="*70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print()
    print("CONTROLES:")
    print("  F9  = INICIAR captura")
    print("  F10 = PARAR captura")
    print("  ESC = SAIR do programa")
    print()
    print("="*70)
    print()
    print("⌨️  Aguardando comandos... (Pressione F9 para iniciar)")
    print()

    # Registrar hotkeys
    keyboard.add_hotkey('f9', on_f9)
    keyboard.add_hotkey('f10', on_f10)
    keyboard.add_hotkey('esc', on_esc)

    print("[+] Conectando ao WebSocket Gateway...")

    # Iniciar loop de captura
    try:
        await capture_loop()
    except KeyboardInterrupt:
        pass

    print()
    print("="*70)
    print("  ✨ Programa Encerrado")
    print("="*70)
    print()
    if frame_count > 0:
        print(f"✓ Total: {frame_count} frames capturados")
        print()
        print("📊 Verifique os resultados:")
        print("   1. Terminal do backend - logs de detecção")
        print("   2. backend/exports/ - Excel com estatísticas")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print()
        print("Programa encerrado.")
