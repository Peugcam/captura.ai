"""
Script para pegar frames do gateway LOCAL e enviar para backend na NUVEM
Roda junto com o gateway que você já usa no OBS
"""
import requests
import time
import base64

GATEWAY_LOCAL = "http://localhost:8000"
BACKEND_CLOUD = "https://gta-analytics-v2.fly.dev"

print("🚀 Iniciando envio de frames para nuvem...")
print(f"📡 Gateway local: {GATEWAY_LOCAL}")
print(f"☁️  Backend nuvem: {BACKEND_CLOUD}")

while True:
    try:
        # Pegar frames do gateway local
        response = requests.get(f"{GATEWAY_LOCAL}/frames", timeout=2)

        if response.status_code == 200:
            frames = response.json()

            if frames and len(frames) > 0:
                print(f"📸 Recebidos {len(frames)} frames do gateway local")

                # Enviar cada frame para a nuvem
                for frame in frames:
                    try:
                        # Decodificar base64 para enviar como file
                        image_data = base64.b64decode(frame['data'])

                        files = {'file': ('frame.jpg', image_data, 'image/jpeg')}

                        cloud_response = requests.post(
                            f"{BACKEND_CLOUD}/api/frames/upload",
                            files=files,
                            timeout=5
                        )

                        if cloud_response.status_code == 200:
                            print(f"✅ Frame enviado para nuvem com sucesso")
                        else:
                            print(f"❌ Erro ao enviar: {cloud_response.status_code}")

                    except Exception as e:
                        print(f"❌ Erro no frame: {e}")

        time.sleep(1)  # Verificar a cada 1 segundo

    except requests.exceptions.ConnectionError:
        print("⚠️ Gateway local não está rodando. Aguardando...")
        time.sleep(5)
    except Exception as e:
        print(f"❌ Erro: {e}")
        time.sleep(2)
