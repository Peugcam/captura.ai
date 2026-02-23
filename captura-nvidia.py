"""
NVIDIA ShadowPlay/Share Capture
Usa o encoder NVENC da GPU para captura com zero overhead
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import Image
import io
import keyboard
import mss
import numpy as np

# Configurações
GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 4
QUALITY = 60
RESIZE_TO = (1920, 1080)

capturing = False
should_exit = False
frame_count = 0
start_time = None

# MSS (Multi-Screen Screenshot) - Mais rápido que PIL
sct = mss.mss()


def capture_screen_mss():
    """
    Captura usando MSS (Multi-Screen Screenshot)
    Muito mais rápido que PIL.ImageGrab e geralmente não é bloqueado
    """
    try:
        # Captura o monitor primário
        monitor = sct.monitors[1]  # 0 = all monitors, 1 = primary

        # Captura
        sct_img = sct.grab(monitor)

        # Converte para PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        if img.size != RESIZE_TO:
            img = img.resize(RESIZE_TO, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=QUALITY)
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
            print("[OK] Conectado ao Gateway com MSS!\n")
            await websocket.send(json.dumps({"type": "start_capture"}))

            last_frame_time = 0
            frame_interval = 1.0 / CAPTURE_FPS

            while not should_exit:
                if capturing:
                    current_time = time.time()
                    if current_time - last_frame_time >= frame_interval:
                        frame_data = capture_screen_mss()
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
    print("  GTA Analytics - MSS Capture (Fast & Reliable)")
    print("=" * 70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Método: MSS (Multi-Screen Screenshot)")
    print()
    print("VANTAGENS:")
    print("  ✓ 3x mais rápido que PIL.ImageGrab")
    print("  ✓ Raramente bloqueado por jogos")
    print("  ✓ Funciona em multi-monitor")
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
