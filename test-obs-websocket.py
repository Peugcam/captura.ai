"""
Teste Rapido: Verifica se OBS consegue capturar GTA
"""
import sys
import io

# Fix encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("  TESTE: OBS WebSocket - Captura de GTA")
print("=" * 70)
print()
print("Este script testa se o OBS consegue capturar o GTA sem tela preta.")
print()
print("REQUISITOS:")
print("  1. OBS Studio instalado e aberto")
print("  2. WebSocket ativado (Tools -> WebSocket Server Settings)")
print("  3. Source configurada para capturar GTA")
print()
print("=" * 70)
print()

# Verificar se biblioteca está instalada
try:
    from obswebsocket import obsws, requests as obs_requests
    print("✓ Biblioteca obs-websocket-py instalada")
except ImportError:
    print("❌ Biblioteca não instalada!")
    print()
    print("Execute: pip install obs-websocket-py")
    print()
    sys.exit(1)

import base64
import io
from PIL import Image

# Configuração
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Deixe vazio se não configurou senha

print()
print(f"Conectando em OBS WebSocket ({OBS_HOST}:{OBS_PORT})...")

try:
    # Conectar
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    ws.connect()
    print("✓ Conectado ao OBS!")
    print()

    # Listar sources disponíveis
    print("Sources disponíveis no OBS:")
    print("-" * 70)

    scenes = ws.call(obs_requests.GetSceneList())
    current_scene = scenes.getCurrentProgramSceneName()

    print(f"Cena atual: {current_scene}")
    print()

    scene_items = ws.call(obs_requests.GetSceneItemList(sceneName=current_scene))
    sources = scene_items.getSceneItems()

    if not sources:
        print("⚠️  Nenhuma source encontrada na cena atual!")
        print()
        print("SOLUÇÃO:")
        print("  1. Abra o OBS")
        print("  2. Adicione uma source (Game Capture ou Display Capture)")
        print("  3. Execute este script novamente")
        ws.disconnect()
        sys.exit(1)

    print(f"Encontradas {len(sources)} sources:")
    for i, item in enumerate(sources, 1):
        source_name = item['sourceName']
        print(f"  {i}. {source_name}")

    print()
    print("-" * 70)
    print()

    # Tentar capturar screenshot de cada source
    print("Testando captura de frames...")
    print()

    for item in sources:
        source_name = item['sourceName']
        print(f"Testando: {source_name}")

        try:
            # Capturar screenshot
            screenshot = ws.call(obs_requests.GetSourceScreenshot(
                sourceName=source_name,
                imageFormat="jpg",
                imageWidth=1920,
                imageHeight=1080,
                imageCompressionQuality=85
            ))

            # Processar imagem
            img_data = screenshot.getImageData()

            # Remove prefixo "data:image/jpg;base64,"
            if ',' in img_data:
                img_data = img_data.split(',', 1)[1]

            img_bytes = base64.b64decode(img_data)
            img = Image.open(io.BytesIO(img_bytes))

            # Verificar se está preto
            pixels = list(img.getdata())[:1000]  # Amostra de 1000 pixels
            avg_brightness = sum([sum(p)/3 for p in pixels]) / len(pixels)

            size_kb = len(img_bytes) / 1024

            print(f"   Tamanho: {size_kb:.1f}KB")
            print(f"   Resolução: {img.size}")
            print(f"   Brilho médio: {avg_brightness:.1f}/255")

            if avg_brightness < 10:
                print(f"   ❌ TELA PRETA! (brilho muito baixo)")
                print(f"      Esta source NÃO está capturando corretamente")
            else:
                print(f"   ✓ Frame OK! Captura funcionando")

                # Salvar frame
                filename = f"obs_test_{source_name.replace(' ', '_')}.jpg"
                img.save(filename)
                print(f"   ✓ Frame salvo em: {filename}")

            print()

        except Exception as e:
            print(f"   ❌ Erro ao capturar: {e}")
            print()

    ws.disconnect()

    print("=" * 70)
    print("  TESTE CONCLUÍDO")
    print("=" * 70)
    print()
    print("INTERPRETAÇÃO:")
    print()
    print("✓ Frame OK = OBS está capturando corretamente")
    print("  → WebSocket vai funcionar para enviar frames")
    print("  → Você pode usar OBS como fonte de captura")
    print()
    print("❌ Tela Preta = OBS está bloqueado")
    print("  → WebSocket NÃO vai resolver o problema")
    print("  → Use Desktop App (Electron/PyInstaller)")
    print()
    print("Frames de teste foram salvos na pasta atual.")
    print("Abra os arquivos .jpg para conferir visualmente.")
    print()

except ConnectionRefusedError:
    print("❌ Não foi possível conectar ao OBS!")
    print()
    print("POSSÍVEIS CAUSAS:")
    print()
    print("1. OBS Studio não está aberto")
    print("   Solução: Abra o OBS Studio")
    print()
    print("2. WebSocket não está ativado")
    print("   Solução:")
    print("   - Abra OBS Studio")
    print("   - Tools → WebSocket Server Settings")
    print("   - Enable WebSocket Server ✓")
    print("   - Apply")
    print()
    print("3. Porta incorreta")
    print(f"   Verificar se OBS usa porta {OBS_PORT}")
    print()

except Exception as e:
    print(f"❌ Erro: {e}")
    print()
    print("Verifique:")
    print("  1. OBS Studio está aberto")
    print("  2. WebSocket está ativado")
    print("  3. Senha (se configurou)")
    print()

print("=" * 70)
