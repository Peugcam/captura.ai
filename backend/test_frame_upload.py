"""
Teste de upload e processamento de frame
Envia um frame real para o backend e verifica resposta
"""
import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import time

def create_test_frame_with_killfeed():
    """Cria um frame de teste com kill feed falso"""
    # Criar imagem 1920x1080
    img = Image.new('RGB', (1920, 1080), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)

    # Simular kill feed no canto superior direito
    # Posição: x=1400-1920, y=0-400 (onde o sistema busca)

    # Texto grande para simular kill feed
    kill_text = "PPP.player KILLED LLL.victim"

    # Desenhar no canto superior direito
    draw.text((1450, 50), kill_text, fill=(255, 255, 255))
    draw.text((1450, 100), "MTL.sniper SNIPED 97m", fill=(255, 200, 200))
    draw.text((1450, 150), "EMPI.assassin eliminated", fill=(255, 255, 255))

    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)

    return buffer

def upload_frame(server_url, frame_data):
    """Envia frame para o servidor"""
    try:
        files = {'file': ('frame.jpg', frame_data, 'image/jpeg')}

        print(f"📤 Enviando frame para {server_url}")
        start = time.time()

        response = requests.post(
            f"{server_url}/api/frames/upload",
            files=files,
            timeout=30
        )

        elapsed = time.time() - start

        print(f"⏱️  Tempo: {elapsed:.2f}s")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            print(f"✅ Resposta: {response.text}")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 TEST FRAME UPLOAD - GTA Analytics")
    print("="*60)

    # Servidor
    SERVER = "https://gta-analytics-v2.fly.dev"

    print("\n1️⃣ Criando frame de teste com kill feed falso...")
    frame = create_test_frame_with_killfeed()
    print("✅ Frame criado (1920x1080)")

    print("\n2️⃣ Enviando para o servidor...")
    success = upload_frame(SERVER, frame)

    print("\n" + "="*60)
    if success:
        print("✅ TESTE PASSOU!")
        print("\n💡 Agora verifique:")
        print("   1. Logs do servidor Fly.io")
        print("   2. Dashboard em https://gta-analytics-v2.fly.dev/strategist")
    else:
        print("❌ TESTE FALHOU!")
        print("\n💡 Próximos passos:")
        print("   1. Verificar logs: fly logs -a gta-analytics-v2")
        print("   2. Verificar se backend está processando frames")
    print("="*60)
