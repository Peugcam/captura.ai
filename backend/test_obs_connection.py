"""
Teste de Conexao OBS WebSocket
================================
Conecta ao OBS via websocket e envia frames para o gateway
"""

import asyncio
import websockets
import httpx
import json
import base64
from datetime import datetime

# Configuracoes
OBS_WS_URL = "ws://localhost:4455"  # Porta padrao do obs-websocket
OBS_PASSWORD = ""  # Deixe vazio se nao tiver senha
GATEWAY_URL = "http://localhost:8000"


async def test_obs_connection():
    """Testa conexao com OBS websocket"""
    print("\n" + "="*70)
    print("TESTE DE CONEXAO OBS WEBSOCKET")
    print("="*70)

    print(f"\nTentando conectar ao OBS em {OBS_WS_URL}...")

    try:
        async with websockets.connect(OBS_WS_URL) as websocket:
            print("OK - Conectado ao OBS WebSocket!")

            # Recebe mensagem de identificacao
            response = await websocket.recv()
            data = json.loads(response)
            print(f"OBS versao: {data.get('d', {}).get('obsWebSocketVersion', 'unknown')}")

            # Envia identificacao
            identify = {
                "op": 1,
                "d": {
                    "rpcVersion": 1
                }
            }

            if OBS_PASSWORD:
                # Autenticacao se necessario
                pass

            await websocket.send(json.dumps(identify))

            # Aguarda confirmacao
            response = await websocket.recv()
            print("OK - Autenticacao bem sucedida")

            # Solicita screenshot
            print("\nSolicitando screenshot do OBS...")
            request = {
                "op": 6,
                "d": {
                    "requestType": "GetSourceScreenshot",
                    "requestId": "test-1",
                    "requestData": {
                        "sourceName": "Cena",  # Nome da cena/fonte
                        "imageFormat": "jpg",
                        "imageWidth": 1920,
                        "imageHeight": 1080
                    }
                }
            }

            await websocket.send(json.dumps(request))

            # Aguarda resposta
            response = await websocket.recv()
            data = json.loads(response)

            if data.get('d', {}).get('requestStatus', {}).get('result'):
                image_data = data['d']['responseData']['imageData']
                # Remove prefixo data:image/jpeg;base64,
                if ',' in image_data:
                    image_data = image_data.split(',')[1]

                print(f"OK - Recebeu screenshot ({len(image_data)} bytes)")

                # Envia para o gateway
                print("\nEnviando frame para o gateway...")
                async with httpx.AsyncClient() as client:
                    payload = {
                        "frames": [{
                            "data": image_data,
                            "timestamp": datetime.now().isoformat()
                        }]
                    }

                    response = await client.post(
                        f"{GATEWAY_URL}/upload",
                        json=payload
                    )

                    if response.status_code == 200:
                        print("OK - Frame enviado para o gateway!")
                    else:
                        print(f"ERRO - Gateway retornou {response.status_code}")

            else:
                print("ERRO - OBS nao retornou screenshot")
                print("Verifique se existe uma cena chamada 'Cena'")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"ERRO - OBS WebSocket nao esta rodando na porta 4455")
        print(f"       Verifique em Ferramentas > obs-websocket Settings")
    except ConnectionRefusedError:
        print(f"ERRO - Nao foi possivel conectar ao OBS")
        print(f"       Verifique se o OBS esta rodando")
    except Exception as e:
        print(f"ERRO - {e}")


async def test_gateway_upload():
    """Testa upload direto ao gateway com frame fake"""
    print("\n" + "="*70)
    print("TESTE DE UPLOAD DIRETO AO GATEWAY")
    print("="*70)

    print("\nCriando frame de teste...")

    # Cria um frame fake (imagem pequena em base64)
    # 1x1 pixel vermelho em JPEG
    fake_image = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"
    fake_image += "HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy"
    fake_image += "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEB"
    fake_image += "AxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAA"
    fake_image += "AAAAAAAAAAAAAAAAAAAH/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AVB//2Q=="

    payload = {
        "frames": [{
            "data": fake_image,
            "timestamp": datetime.now().isoformat()
        }]
    }

    print("Enviando frame fake para o gateway...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GATEWAY_URL}/upload",
                json=payload,
                timeout=5.0
            )

            if response.status_code == 200:
                print("OK - Gateway aceitou o frame!")
                print(f"Resposta: {response.json()}")
            else:
                print(f"ERRO - Gateway retornou {response.status_code}")
                print(f"Resposta: {response.text}")

    except Exception as e:
        print(f"ERRO - {e}")


async def test_polling():
    """Testa se consegue recuperar frames via polling"""
    print("\n" + "="*70)
    print("TESTE DE POLLING")
    print("="*70)

    print("\nFazendo polling do gateway...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/poll", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                frames = data.get('frames', [])
                print(f"OK - Polling funcionando ({len(frames)} frames na fila)")

                if frames:
                    print(f"\nPrimeiro frame:")
                    print(f"  Timestamp: {frames[0].get('timestamp', 'N/A')}")
                    print(f"  Tamanho: {len(frames[0].get('data', ''))} bytes")
                else:
                    print("  Fila vazia (gateway nao recebeu frames ainda)")
            else:
                print(f"ERRO - Polling retornou {response.status_code}")

    except Exception as e:
        print(f"ERRO - {e}")


async def main():
    print("="*70)
    print("SUITE DE TESTES - CONEXAO OBS")
    print("="*70)

    # Teste 1: Upload direto
    await test_gateway_upload()

    # Teste 2: Polling
    await test_polling()

    # Teste 3: Conexao OBS
    await test_obs_connection()

    print("\n" + "="*70)
    print("TESTES CONCLUIDOS")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
