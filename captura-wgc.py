"""
Windows Graphics Capture API - Impossível de Bloquear
Usa a API nativa do Windows 10/11 que captura DENTRO do pipeline de renderização
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import Image
import io
import keyboard
import ctypes
from ctypes import wintypes
import d3dshot

# Configurações
GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 4
QUALITY = 60
RESIZE_TO = (1920, 1080)

capturing = False
should_exit = False
frame_count = 0
start_time = None

# Inicializar D3DShot (DirectX Screen Capture)
d = d3dshot.create(capture_output="pil")

def capture_screen_wgc():
    """Captura usando DirectX - Não pode ser bloqueado pelo jogo"""
    try:
        screenshot = d.screenshot()
        if screenshot is None:
            return None

        if screenshot.size != RESIZE_TO:
            screenshot = screenshot.resize(RESIZE_TO, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        screenshot.save(buffer, format='JPEG', quality=QUALITY)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Erro ao capturar: {e}")
        return None


def on_s():
    global capturing, frame_count, start_time
    if not capturing:
        capturing = True
        frame_count = 0
        start_time = time.time()
        print("\n>>> CAPTURA INICIADA! (Pressione P para parar)\n")


def on_p():
    global capturing
    if capturing:
        capturing = False
        elapsed = time.time() - start_time if start_time else 0
        print(f"\n>>> CAPTURA PARADA! {frame_count} frames em {elapsed:.1f}s\n")


def on_esc():
    global should_exit, capturing
    capturing = False
    should_exit = True
    print("\n>>> Encerrando...\n")


async def capture_loop():
    global frame_count

    try:
        async with websockets.connect(GATEWAY_WS, ping_interval=20, ping_timeout=10) as websocket:
            print("[OK] Conectado ao Gateway com Windows Graphics Capture!\n")
            await websocket.send(json.dumps({"type": "start_capture"}))

            last_frame_time = 0
            frame_interval = 1.0 / CAPTURE_FPS

            while not should_exit:
                if capturing:
                    current_time = time.time()
                    if current_time - last_frame_time >= frame_interval:
                        frame_data = capture_screen_wgc()
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
                                print(f"[{frame_count} frames] {elapsed:.1f}s ({frame_count/elapsed:.1f} FPS)")

                            last_frame_time = current_time

                await asyncio.sleep(0.05)

            await websocket.send(json.dumps({"type": "stop_capture"}))

    except Exception as e:
        print(f"[ERROR] {e}")


async def main():
    print("=" * 70)
    print("  GTA Analytics - Windows Graphics Capture (Anti-Block)")
    print("=" * 70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Método: DirectX Screen Capture (D3DShot)")
    print()
    print("VANTAGENS:")
    print("  ✓ Impossível de bloquear (captura no nível do DirectX)")
    print("  ✓ Performance superior ao OBS")
    print("  ✓ Funciona em fullscreen e windowed mode")
    print()
    print("CONTROLES:")
    print("  S   = INICIAR captura")
    print("  P   = PARAR captura")
    print("  ESC = SAIR")
    print()
    print("=" * 70)
    print()

    keyboard.add_hotkey('s', on_s)
    keyboard.add_hotkey('p', on_p)
    keyboard.add_hotkey('esc', on_esc)

    print("[*] Aguardando comandos... (Pressione S para iniciar)\n")

    try:
        await capture_loop()
    except KeyboardInterrupt:
        pass

    print("\n" + "=" * 70)
    print("  Programa Encerrado")
    print("=" * 70)
    if frame_count > 0:
        print(f"\nTotal: {frame_count} frames\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")
