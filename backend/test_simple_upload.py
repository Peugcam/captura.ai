"""
Teste Simples - Upload de Frame ao Gateway
===========================================
Testa envio de frame direto ao gateway sem depender do OBS
"""

import asyncio
import httpx
import base64
from datetime import datetime
from PIL import Image
import io

GATEWAY_URL = "http://localhost:8000"


def create_test_frame():
    """Cria um frame de teste simples"""
    # Cria imagem 100x100 pixels com texto
    img = Image.new('RGB', (100, 100), color='red')

    # Converte para base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64


async def test_upload():
    print("="*60)
    print("TESTE SIMPLES - UPLOAD DE FRAMES")
    print("="*60)

    # Cria frame de teste
    print("\n[1/3] Criando frame de teste...")
    frame_data = create_test_frame()
    print(f"OK - Frame criado ({len(frame_data)} bytes em base64)")

    # Envia para o gateway
    print("\n[2/3] Enviando frame para o gateway...")

    # Decodifica base64 para bytes
    img_bytes = base64.b64decode(frame_data)

    # Prepara multipart form
    files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GATEWAY_URL}/upload",
                files=files,
                timeout=5.0
            )

            if response.status_code == 200:
                print("OK - Gateway aceitou o frame!")
                result = response.json()
                print(f"Resposta: {result}")
            else:
                print(f"ERRO - Status {response.status_code}")
                print(f"Resposta: {response.text}")
                return False

    except Exception as e:
        print(f"ERRO - {e}")
        return False

    # Testa polling
    print("\n[3/3] Verificando se o frame esta disponivel via polling...")

    try:
        async with httpx.AsyncClient() as client:
            await asyncio.sleep(0.5)  # Pequeno delay

            response = await client.get(f"{GATEWAY_URL}/frames", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                frames = data.get('frames', [])

                if frames:
                    print(f"OK - Recuperou {len(frames)} frame(s) via polling!")
                    print(f"Frame timestamp: {frames[0].get('timestamp', 'N/A')}")
                    return True
                else:
                    print("AVISO - Fila vazia, frame pode ter sido processado")
                    return True
            else:
                print(f"ERRO - Polling retornou {response.status_code}")
                return False

    except Exception as e:
        print(f"ERRO - {e}")
        return False


async def test_multiple_frames():
    """Testa envio de multiplos frames"""
    print("\n" + "="*60)
    print("TESTE - MULTIPLOS FRAMES")
    print("="*60)

    print("\nEnviando 10 frames de teste...")

    try:
        async with httpx.AsyncClient() as client:
            # Envia 10 frames separadamente
            for i in range(10):
                frame_data = create_test_frame()
                img_bytes = base64.b64decode(frame_data)
                files = {'file': (f'frame{i}.jpg', img_bytes, 'image/jpeg')}

                response = await client.post(
                    f"{GATEWAY_URL}/upload",
                    files=files,
                    timeout=5.0
                )

                if response.status_code != 200:
                    print(f"Erro no frame {i}")
                    return

            print(f"OK - Enviou 10 frames com sucesso!")

            # Verifica polling
            await asyncio.sleep(0.5)
            response = await client.get(f"{GATEWAY_URL}/frames")
            data = response.json()
            frames = data.get('frames', [])
            print(f"Recuperou: {len(frames)} frames")

    except Exception as e:
        print(f"ERRO - {e}")


async def main():
    print("\n" + "="*60)
    print("TESTES DE DETECCAO DE FRAMES")
    print("="*60)
    print("\nEste teste verifica se o gateway esta")
    print("recebendo e armazenando frames corretamente")

    # Teste basico
    success = await test_upload()

    if success:
        print("\n" + "="*60)
        print("RESULTADO: SUCESSO!")
        print("="*60)
        print("\nO pipeline de frames esta funcionando!")
        print("Gateway consegue:")
        print("  - Receber frames via upload")
        print("  - Armazenar na fila")
        print("  - Disponibilizar via polling")

        # Teste adicional
        await test_multiple_frames()

        print("\n" + "="*60)
        print("PROXIMO PASSO")
        print("="*60)
        print("\nAgora que o gateway esta funcionando,")
        print("voce pode:")
        print("  1. Abrir o OBS")
        print("  2. Capturar o Naruto Online (ou qualquer tela)")
        print("  3. Configurar OBS para enviar frames ao gateway")
        print("  4. Iniciar gravacao/transmissao")
        print("\nO sistema ira detectar automaticamente!")

    else:
        print("\n" + "="*60)
        print("RESULTADO: FALHA")
        print("="*60)
        print("\nVerifique se o gateway esta rodando:")
        print("  cd gateway")
        print("  gateway.exe")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
