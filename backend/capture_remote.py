"""
GTA Analytics - Cliente de Captura Remoto
==========================================
Captura GTA V e envia para Fly.dev (gta-analytics-v2.fly.dev)
SEM OBS! Usa D3DShot direto para contornar bloqueio do GTA.

CUSTO: $0 (usa Gemini Flash 2.0 FREE via OpenRouter)

Autor: Paulo Eugenio Campos
"""

import d3dshot
import time
import httpx
import base64
import io
import asyncio
from PIL import Image
from datetime import datetime
import sys

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Servidor Fly.dev (já configurado!)
SERVER_URL = "https://gta-analytics-v2.fly.dev/api/frames/upload"

# Smart Sampling (economia massiva)
CAPTURE_INTERVAL = 2.0  # 1 frame a cada 2 segundos = 0.5 FPS
# Kill feed dura ~5 segundos na tela, então 0.5 FPS captura perfeitamente!

# Qualidade JPEG (85 = ótimo balanço qualidade/tamanho)
JPEG_QUALITY = 85

# API Key (opcional - remova se não quiser autenticação)
API_KEY = None  # ou "seu-api-key-aqui"

# ============================================================================
# ESTATÍSTICAS
# ============================================================================

frames_sent = 0
frames_failed = 0
bytes_sent = 0
start_time = None

# ============================================================================
# FUNÇÕES
# ============================================================================

async def send_frame_to_server(frame_data):
    """
    Envia frame para Fly.dev via HTTP multipart

    Args:
        frame_data: NumPy array do frame (do D3DShot)

    Returns:
        True se enviou com sucesso, False caso contrário
    """
    global frames_sent, frames_failed, bytes_sent

    try:
        # Encode para JPEG
        img = Image.fromarray(frame_data)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=JPEG_QUALITY)
        img_bytes = buffer.getvalue()

        # Preparar upload multipart
        files = {'file': ('frame.jpg', img_bytes, 'image/jpeg')}

        # Headers (com API key se configurada)
        headers = {}
        if API_KEY:
            headers['X-API-Key'] = API_KEY

        # Enviar para servidor
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                SERVER_URL,
                files=files,
                headers=headers
            )

            if response.status_code == 200:
                frames_sent += 1
                bytes_sent += len(img_bytes)
                size_kb = len(img_bytes) // 1024

                # Calcular stats
                uptime = int(time.time() - start_time)
                fps_avg = frames_sent / uptime if uptime > 0 else 0

                now = datetime.now().strftime('%H:%M:%S')
                print(f"[{now}] ✅ Frame {frames_sent} enviado ({size_kb} KB) | "
                      f"Uptime: {uptime}s | FPS médio: {fps_avg:.2f}")

                return True
            else:
                frames_failed += 1
                print(f"❌ Erro {response.status_code}: {response.text[:100]}")
                return False

    except httpx.TimeoutException:
        frames_failed += 1
        print(f"⏱️  Timeout ao enviar frame (servidor lento ou sem internet)")
        return False
    except Exception as e:
        frames_failed += 1
        print(f"❌ Erro ao enviar: {e}")
        return False


async def main():
    """Loop principal de captura e envio"""
    global start_time

    print("="*70)
    print("GTA ANALYTICS - CAPTURA REMOTA")
    print("="*70)
    print(f"\n📡 Servidor: {SERVER_URL}")
    print(f"⏱️  Intervalo: {CAPTURE_INTERVAL}s (smart sampling)")
    print(f"📸 Qualidade: {JPEG_QUALITY}")
    print(f"💰 Custo: $0 (Gemini Flash FREE via OpenRouter)")
    print("\n" + "="*70)

    # Inicializar D3DShot
    print("\n🔧 Inicializando captura DirectX...")
    try:
        d = d3dshot.create()
        print("✅ D3DShot inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar D3DShot: {e}")
        print("\n💡 Certifique-se que você tem:")
        print("   - GPU NVIDIA ou AMD")
        print("   - Drivers atualizados")
        print("   - Python 3.8+")
        print("\n   Instale: pip install d3dshot")
        return

    print("\n⏳ Aguardando GTA V iniciar...")
    print("   (A captura começará automaticamente quando detectar o jogo)\n")
    print("💡 Pressione Ctrl+C para parar\n")
    print("="*70 + "\n")

    start_time = time.time()
    consecutive_failures = 0

    try:
        while True:
            try:
                # Capturar frame do GTA
                frame = d.screenshot()

                if frame is not None:
                    # GTA detectado! Enviar para servidor
                    success = await send_frame_to_server(frame)

                    if success:
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1

                        # Avisar se muitas falhas consecutivas
                        if consecutive_failures >= 5:
                            print(f"\n⚠️  ATENÇÃO: {consecutive_failures} falhas consecutivas!")
                            print("   Verifique:")
                            print("   - Conexão com internet")
                            print("   - Servidor Fly.dev online")
                            print("   - Firewall não bloqueando\n")
                            consecutive_failures = 0  # Reset para não spammar

                else:
                    # GTA não detectado (pode estar minimizado ou fechado)
                    if frames_sent == 0:
                        # Ainda não capturou nenhum frame
                        print("⏳ Aguardando GTA V... (certifique-se que está rodando)")
                    else:
                        # Já capturou antes, provavelmente minimizou
                        print("⚠️  GTA não detectado (minimizado ou fechado?)")

                # Smart sampling: aguardar intervalo
                await asyncio.sleep(CAPTURE_INTERVAL)

            except KeyboardInterrupt:
                raise  # Propagar para o except externo
            except Exception as e:
                print(f"❌ Erro no loop principal: {e}")
                await asyncio.sleep(CAPTURE_INTERVAL)

    except KeyboardInterrupt:
        # Usuário parou (Ctrl+C)
        print("\n\n" + "="*70)
        print("RESUMO DA SESSÃO")
        print("="*70)

        uptime = int(time.time() - start_time)
        total_frames = frames_sent + frames_failed
        success_rate = (frames_sent / total_frames * 100) if total_frames > 0 else 0
        avg_fps = frames_sent / uptime if uptime > 0 else 0
        mb_sent = bytes_sent / (1024 * 1024)

        print(f"\n⏱️  Tempo total: {uptime}s ({uptime//60}min {uptime%60}s)")
        print(f"📸 Frames enviados: {frames_sent}")
        print(f"❌ Frames falhos: {frames_failed}")
        print(f"✅ Taxa de sucesso: {success_rate:.1f}%")
        print(f"📊 FPS médio: {avg_fps:.2f}")
        print(f"📦 Dados enviados: {mb_sent:.2f} MB")
        print(f"💰 Custo total: $0.00 (Gemini Flash FREE)")

        if frames_sent > 0:
            print(f"\n🎉 SUCESSO! {frames_sent} frames processados no servidor!")
            print(f"   Dashboard: https://gta-analytics-v2.fly.dev/strategist")
        else:
            print(f"\n⚠️  Nenhum frame foi enviado.")
            print(f"   Verifique se GTA V estava rodando e visível.")

        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando...\n")
        sys.exit(0)
