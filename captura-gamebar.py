"""
Windows Game Bar Capture
Usa a API do Game Bar do Windows (Win+G)
"""
import asyncio
import websockets
import json
import base64
import time
from PIL import Image
import io
import keyboard
import win32gui
import win32ui
import win32con
from ctypes import windll

# Configurações
GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 4
QUALITY = 60
RESIZE_TO = (1920, 1080)

capturing = False
should_exit = False
frame_count = 0
start_time = None


def capture_window_gdi(window_name=None):
    """
    Captura usando Windows GDI (Graphics Device Interface)
    Método de baixo nível que bypassa proteções de jogos
    """
    try:
        # Se não especificar janela, captura tela toda
        if window_name:
            hwnd = win32gui.FindWindow(None, window_name)
        else:
            hwnd = win32gui.GetDesktopWindow()

        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # Create device context
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # Create bitmap
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        # Capture
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        # Convert to PIL Image
        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)

        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        # Cleanup
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

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
            print("[OK] Conectado ao Gateway com Windows GDI!\n")
            await websocket.send(json.dumps({"type": "start_capture"}))

            last_frame_time = 0
            frame_interval = 1.0 / CAPTURE_FPS

            while not should_exit:
                if capturing:
                    current_time = time.time()
                    if current_time - last_frame_time >= frame_interval:
                        # Tente capturar janela do GTA, se falhar captura desktop
                        frame_data = capture_window_gdi("Grand Theft Auto V")
                        if not frame_data:
                            frame_data = capture_window_gdi()  # Fallback para desktop

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
    print("  GTA Analytics - Windows GDI Capture (Low-Level)")
    print("=" * 70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Método: Windows GDI PrintWindow")
    print()
    print("VANTAGENS:")
    print("  ✓ Captura direta da janela do jogo")
    print("  ✓ Bypassa proteções anti-screenshot")
    print("  ✓ Funciona mesmo com jogo minimizado")
    print()
    print("NOTA: Se o jogo bloquear GDI, tente captura-wgc.py ou captura-nvidia.py")
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
    print("[*] Tentando capturar janela 'Grand Theft Auto V'...\n")

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
