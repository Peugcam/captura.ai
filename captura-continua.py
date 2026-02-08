"""
Naruto Online Combat Analyzer - Captura Contínua Robusta
==========================================================
Mantém conexão WebSocket ativa e reconecta automaticamente.

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
import sys

GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 4
QUALITY = 60
RESIZE_TO = (1920, 1080)

# Controle
capturing = False
should_exit = False
frame_count = 0
start_time = None
total_frames_sent = 0


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
        print("==> CAPTURA INICIADA! (Pressione F10 para parar)")
        print()


def on_f10():
    """Callback para F10 - Parar"""
    global capturing
    if capturing:
        capturing = False
        elapsed = time.time() - start_time if start_time else 0
        print()
        print("==> CAPTURA PARADA!")
        print(f"    {frame_count} frames capturados em {elapsed:.1f}s")
        print()


def on_esc():
    """Callback para ESC - Sair"""
    global should_exit, capturing
    capturing = False
    should_exit = True
    print()
    print("==> Encerrando programa...")


async def capture_with_reconnect():
    """Loop de captura com reconexão automática"""
    global frame_count, total_frames_sent

    reconnect_delay = 2
    last_frame_time = 0
    frame_interval = 1.0 / CAPTURE_FPS

    while not should_exit:
        try:
            print(f"[*] Conectando ao WebSocket Gateway...")
            async with websockets.connect(GATEWAY_WS, ping_interval=20, ping_timeout=10) as websocket:
                print("[OK] Conectado com sucesso!")
                print()

                await websocket.send(json.dumps({"type": "start_capture"}))

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

                                try:
                                    await websocket.send(json.dumps(frame_msg))
                                    frame_count += 1
                                    total_frames_sent += 1

                                    if frame_count % 10 == 0:
                                        elapsed = time.time() - start_time
                                        fps = frame_count / elapsed if elapsed > 0 else 0
                                        print(f"[{frame_count} frames] {elapsed:.1f}s | FPS: {fps:.1f}")

                                    last_frame_time = current_time
                                except websockets.exceptions.ConnectionClosed:
                                    print("[!] Conexão perdida durante envio")
                                    break

                    await asyncio.sleep(0.05)

                # Enviar stop_capture antes de desconectar
                try:
                    await websocket.send(json.dumps({"type": "stop_capture"}))
                except:
                    pass

        except websockets.exceptions.WebSocketException as e:
            if not should_exit:
                print(f"[!] Erro WebSocket: {e}")
                print(f"[*] Reconectando em {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 1.5, 30)  # Backoff exponencial
        except Exception as e:
            if not should_exit:
                print(f"[ERROR] Erro inesperado: {e}")
                await asyncio.sleep(reconnect_delay)


async def main():
    """Função principal"""
    print("=" * 70)
    print("  Naruto Online Combat Analyzer - Captura Contínua")
    print("=" * 70)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print()
    print("CONTROLES:")
    print("  F9  = INICIAR captura")
    print("  F10 = PARAR captura")
    print("  ESC = SAIR do programa")
    print()
    print("=" * 70)
    print()

    # Registrar hotkeys
    keyboard.add_hotkey('f9', on_f9)
    keyboard.add_hotkey('f10', on_f10)
    keyboard.add_hotkey('esc', on_esc)

    print("[*] Aguardando comandos... (Pressione F9 para iniciar)")
    print()

    # Iniciar loop de captura com reconexão
    try:
        await capture_with_reconnect()
    except KeyboardInterrupt:
        pass

    print()
    print("=" * 70)
    print("  Programa Encerrado")
    print("=" * 70)
    print()
    if total_frames_sent > 0:
        print(f"Total de frames enviados: {total_frames_sent}")
        print()
        print("Verifique os resultados:")
        print("  1. Terminal do backend - logs de detecção")
        print("  2. Dashboard web - estatísticas em tempo real")
        print("  3. backend/exports/ - Excel com dados completos")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
