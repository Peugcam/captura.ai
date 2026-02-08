"""
GTA Analytics V2 - Live Screen Capture
=======================================
Captura tela em tempo real e envia para o gateway
"""
import asyncio
import websockets
import json
import base64
import time
from datetime import datetime
from PIL import ImageGrab, Image
import io
import keyboard
import sys

# Configurações
GATEWAY_WS = "ws://localhost:8000/ws"
CAPTURE_FPS = 1  # Capturar 1 frame por segundo
QUALITY = 50  # Qualidade JPEG (1-100)
RESIZE_TO = (1920, 1080)  # Redimensionar para otimizar

# Estado
capturing = False
total_frames = 0
start_time = None


def capture_screen_as_base64() -> str:
    """Captura tela e converte para base64"""
    try:
        # Capturar tela inteira
        screenshot = ImageGrab.grab()

        # Redimensionar se necessário
        if screenshot.size != RESIZE_TO:
            screenshot = screenshot.resize(RESIZE_TO, Image.Resampling.LANCZOS)

        # Converter para JPEG base64
        buffer = io.BytesIO()
        screenshot.save(buffer, format='JPEG', quality=QUALITY)
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_base64

    except Exception as e:
        print(f"[ERROR] Erro ao capturar tela: {e}")
        return None


async def send_frames(websocket):
    """Loop de captura e envio de frames"""
    global total_frames, start_time

    interval = 1.0 / CAPTURE_FPS

    print(f"[+] Capturando a {CAPTURE_FPS} FPS")
    print("[i] Pressione 'q' para parar")
    print()

    start_time = time.time()

    while capturing:
        frame_start = time.time()

        # Capturar frame
        frame_data = capture_screen_as_base64()

        if frame_data:
            # Enviar frame
            frame_msg = {
                "type": "frame",
                "data": frame_data,
                "timestamp": int(time.time() * 1000)
            }

            try:
                await websocket.send(json.dumps(frame_msg))
                total_frames += 1

                # Log a cada 10 frames
                if total_frames % 10 == 0:
                    elapsed = time.time() - start_time
                    fps_real = total_frames / elapsed if elapsed > 0 else 0
                    print(f"[{total_frames}] Frames enviados | FPS médio: {fps_real:.2f}")

            except Exception as e:
                print(f"[ERROR] Erro ao enviar frame: {e}")
                break

        # Aguardar próximo frame
        frame_elapsed = time.time() - frame_start
        sleep_time = max(0, interval - frame_elapsed)
        await asyncio.sleep(sleep_time)


def toggle_capture():
    """Toggle captura on/off"""
    global capturing
    capturing = not capturing
    if capturing:
        print("\n[START] Captura iniciada!")
    else:
        print("\n[STOP] Captura parada!")


async def keyboard_listener():
    """Escuta teclas de controle"""
    global capturing

    print("\n[i] Controles:")
    print("    ESPAÇO = Iniciar/Pausar captura")
    print("    Q = Sair")
    print()

    while True:
        try:
            if keyboard.is_pressed('space'):
                toggle_capture()
                await asyncio.sleep(0.5)  # Debounce

            if keyboard.is_pressed('q'):
                print("\n[EXIT] Encerrando...")
                return

            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"[ERROR] Keyboard listener: {e}")
            await asyncio.sleep(0.1)


async def main():
    """Função principal"""
    global capturing

    print("="*60)
    print("  GTA Analytics V2 - Live Screen Capture")
    print("="*60)
    print()
    print(f"Gateway: {GATEWAY_WS}")
    print(f"FPS: {CAPTURE_FPS}")
    print(f"Resolução: {RESIZE_TO}")
    print(f"Qualidade: {QUALITY}")
    print()

    try:
        print("[+] Conectando ao WebSocket Gateway...")
        async with websockets.connect(GATEWAY_WS) as websocket:
            print("[OK] Conectado!")

            # Enviar start_capture
            await websocket.send(json.dumps({
                "type": "start_capture"
            }))

            # Aguardar ack
            response = await websocket.recv()
            print(f"[<-] {response}")
            print()

            # Criar tasks
            keyboard_task = asyncio.create_task(keyboard_listener())

            # Aguardar usuário iniciar captura
            print("[i] Pressione ESPAÇO para iniciar a captura")

            while not capturing:
                await asyncio.sleep(0.1)
                if keyboard_task.done():
                    break

            if not keyboard_task.done():
                # Iniciar captura
                capture_task = asyncio.create_task(send_frames(websocket))

                # Aguardar alguma task terminar
                done, pending = await asyncio.wait(
                    [keyboard_task, capture_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancelar tasks pendentes
                for task in pending:
                    task.cancel()

            # Stop capture
            await websocket.send(json.dumps({
                "type": "stop_capture"
            }))
            print("\n[STOP] Stop capture enviado")

            # Estatísticas finais
            if start_time:
                elapsed = time.time() - start_time
                fps_real = total_frames / elapsed if elapsed > 0 else 0
                print()
                print("="*60)
                print("  Estatísticas")
                print("="*60)
                print(f"Total de frames: {total_frames}")
                print(f"Tempo: {elapsed:.1f}s")
                print(f"FPS médio: {fps_real:.2f}")
                print("="*60)

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[!] Certifique-se que o sistema está rodando:")
        print("   start-system.bat")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[EXIT] Interrompido pelo usuário")
        sys.exit(0)
