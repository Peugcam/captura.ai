"""
Test Mock Frame - Simula envio de frame via WebSocket
"""
import asyncio
import websockets
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import io

def create_mock_frame():
    """Cria um frame fake com kill feed"""
    # Criar imagem 1920x1080
    img = Image.new('RGB', (1920, 1080), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Simular kill feed no canto superior direito
    kill_text = "PPP almeida99 MATOU LLL pikachu1337 120m"
    draw.text((1200, 50), kill_text, fill=(255, 255, 255), font=font)

    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=50)
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64

async def send_test_frames():
    """Envia frames de teste para o gateway"""
    uri = "ws://localhost:8000/ws"

    print("[+] Conectando ao WebSocket Gateway...")

    try:
        async with websockets.connect(uri) as websocket:
            print("[OK] Conectado!")

            # Enviar start_capture
            await websocket.send(json.dumps({
                "type": "start_capture"
            }))
            print("[+] Start capture enviado")

            # Aguardar ack
            response = await websocket.recv()
            print(f"[<-] Resposta: {response}")

            # Criar frame mock
            print("\n[+] Criando frame de teste com kill...")
            frame_data = create_mock_frame()

            # Enviar 5 frames
            for i in range(5):
                frame_msg = {
                    "type": "frame",
                    "data": frame_data,
                    "timestamp": int(asyncio.get_event_loop().time() * 1000)
                }

                await websocket.send(json.dumps(frame_msg))
                print(f"[OK] Frame {i+1}/5 enviado ({len(frame_data)} bytes base64)")

                await asyncio.sleep(1)

            print("\n[OK] Todos os frames enviados!")
            print("[i] Verifique os logs do backend Python para ver o processamento")
            print("[i] Aguarde 2-3 segundos para o batch processing...")

            await asyncio.sleep(5)

            # Stop capture
            await websocket.send(json.dumps({
                "type": "stop_capture"
            }))
            print("\n[STOP] Stop capture enviado")

    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        print("\n[!] Certifique-se que o Go Gateway esta rodando:")
        print("   cd gateway && go run main.go websocket.go buffer.go")

if __name__ == "__main__":
    print("="*60)
    print("  GTA Analytics V2 - Test Mock Frame")
    print("="*60)
    print()

    asyncio.run(send_test_frames())

    print("\n" + "="*60)
    print("  Teste concluído!")
    print("="*60)
