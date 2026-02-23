"""
Captura de tela em background - ZERO interferência visual
Roda em background sem aparecer nada na tela do jogador
"""

import time
import requests
from PIL import ImageGrab
from io import BytesIO
from datetime import datetime

# Configuração
GATEWAY_URL = "https://gta-analytics-gateway.fly.dev"
CAPTURE_INTERVAL = 1  # segundos
QUALITY = 85  # qualidade JPEG (0-100)

# Estatísticas
frames_capturados = 0
frames_enviados = 0
erros = 0

print("=" * 60)
print("🎮 GTA ANALYTICS - CAPTURA EM BACKGROUND")
print("=" * 60)
print(f"Gateway: {GATEWAY_URL}")
print(f"Intervalo: {CAPTURE_INTERVAL}s")
print(f"Qualidade: {QUALITY}%")
print("=" * 60)
print("\n⚠️  IMPORTANTE:")
print("   - Esta janela pode ficar MINIMIZADA")
print("   - NADA aparece na tela do jogo")
print("   - Jogador não vê NENHUMA interferência")
print("   - Para parar: Feche esta janela ou Ctrl+C")
print("\n" + "=" * 60)
print("\nIniciando em 3 segundos...\n")

time.sleep(3)

# Testar conexão
print("🔍 Testando conexão com gateway...")
try:
    response = requests.get(f"{GATEWAY_URL}/health", timeout=5)
    if response.ok:
        print("✅ Gateway online e acessível!\n")
    else:
        print(f"⚠️  Gateway retornou HTTP {response.status_code}")
        print("   Sistema vai tentar enviar mesmo assim...\n")
except Exception as e:
    print(f"⚠️  Não foi possível conectar ao gateway: {e}")
    print("   Sistema vai tentar enviar mesmo assim...\n")

print("📸 Iniciando captura automática...")
print("=" * 60)

try:
    while True:
        try:
            # Capturar tela
            screenshot = ImageGrab.grab()
            frames_capturados += 1

            # Converter para JPEG em memória
            buffer = BytesIO()
            screenshot.save(buffer, format='JPEG', quality=QUALITY)
            buffer.seek(0)

            # Enviar para gateway
            files = {'file': ('frame.jpg', buffer, 'image/jpeg')}
            response = requests.post(
                f"{GATEWAY_URL}/upload",
                files=files,
                timeout=10
            )

            if response.ok:
                frames_enviados += 1
                now = datetime.now().strftime("%H:%M:%S")

                # Log a cada 10 frames
                if frames_enviados % 10 == 0:
                    print(f"[{now}] ✅ {frames_enviados} frames enviados | {erros} erros")
            else:
                erros += 1
                print(f"❌ Erro HTTP {response.status_code}: {response.text[:100]}")

        except requests.exceptions.Timeout:
            erros += 1
            print(f"⏱️  Timeout ao enviar frame (gateway demorou muito)")

        except requests.exceptions.ConnectionError:
            erros += 1
            print(f"🔌 Erro de conexão (gateway offline ou sem internet)")

        except Exception as e:
            erros += 1
            print(f"❌ Erro inesperado: {e}")

        # Aguardar próximo frame
        time.sleep(CAPTURE_INTERVAL)

except KeyboardInterrupt:
    print("\n\n" + "=" * 60)
    print("👋 Encerrando captura...")
    print("=" * 60)
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   📸 Frames capturados: {frames_capturados}")
    print(f"   ☁️  Frames enviados: {frames_enviados}")
    print(f"   ❌ Erros: {erros}")
    if frames_capturados > 0:
        taxa_sucesso = (frames_enviados / frames_capturados) * 100
        print(f"   ✅ Taxa de sucesso: {taxa_sucesso:.1f}%")
    print("\n" + "=" * 60)
