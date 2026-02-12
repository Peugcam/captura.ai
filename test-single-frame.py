#!/usr/bin/env python3
"""
Test single frame detection - Custo: ~$0.001
Captura 1 screenshot e testa detecção de kill
"""

import io
import base64
import asyncio
import sys
from PIL import ImageGrab
import httpx

async def test_single_frame():
    print("\n" + "="*60)
    print("TESTE DE DETECCAO - 1 FRAME")
    print("="*60)
    print("\nPrepare a tela:")
    print("   1. Abra uma imagem/video do GTA com kill feed visivel")
    print("   2. Ou abra o jogo com kills acontecendo")
    print("   3. Pressione ENTER quando estiver pronto...")

    input()

    print("\n📷 Capturando screenshot...")
    screenshot = ImageGrab.grab()

    # Apply ROI (top-right corner where kill feed appears)
    width, height = screenshot.size
    roi_x = int(width * 0.75)
    roi_y = 0
    roi_width = int(width * 0.25)
    roi_height = int(height * 0.35)

    roi_image = screenshot.crop((roi_x, roi_y, roi_x + roi_width, roi_y + roi_height))

    print(f"   Resolução completa: {width}x{height}")
    print(f"   ROI (kill feed): {roi_width}x{roi_height}")

    # Save for inspection
    roi_image.save("test_frame_roi.png")
    print(f"   💾 ROI salvo em: test_frame_roi.png")

    # Encode to base64
    buffer = io.BytesIO()
    roi_image.save(buffer, format="JPEG", quality=85)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"   📦 Tamanho: {len(buffer.getvalue()) / 1024:.1f} KB")

    # Test OCR first
    print("\n🔍 Testando OCR...")
    try:
        import pytesseract
        ocr_text = pytesseract.image_to_string(roi_image, config='--psm 6')
        print(f"   Texto detectado ({len(ocr_text)} chars):")
        print(f"   {ocr_text[:200]}...")

        keywords = ["killed", "kill", "death", "eliminated", "matou"]
        has_keyword = any(kw in ocr_text.lower() for kw in keywords)

        if has_keyword:
            print(f"   ✅ OCR detectou palavra-chave!")
        else:
            print(f"   ⚠️  OCR NÃO detectou palavra-chave (vai enviar para Vision API anyway)")
    except Exception as e:
        print(f"   ⚠️  OCR falhou: {e}")

    # Call Vision API
    print("\n🤖 Chamando Vision API...")
    print("   Modelo: openai/gpt-4o via OpenRouter")
    print("   Custo estimado: ~$0.001")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer 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",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """Analyze this GTA kill feed image and extract ALL kill events.

For EACH kill event, extract:
- killer: player name who got the kill
- victim: player name who was killed
- weapon: weapon used (if visible)
- timestamp: game time if shown

Return ONLY valid JSON array:
[{"killer": "PlayerA", "victim": "PlayerB", "weapon": "AK-47", "timestamp": "12:34"}]

If NO kills visible, return: []"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                print(f"\n✅ Vision API respondeu:")
                print(f"   {content}")

                # Parse kills
                import json
                try:
                    kills = json.loads(content)
                    if kills:
                        print(f"\n🎯 KILLS DETECTADAS: {len(kills)}")
                        for i, kill in enumerate(kills, 1):
                            print(f"\n   Kill #{i}:")
                            print(f"      Killer: {kill.get('killer', 'N/A')}")
                            print(f"      Victim: {kill.get('victim', 'N/A')}")
                            print(f"      Weapon: {kill.get('weapon', 'N/A')}")
                            print(f"      Time: {kill.get('timestamp', 'N/A')}")
                    else:
                        print(f"\n⚠️  Nenhuma kill detectada na imagem")
                except:
                    print(f"\n⚠️  Resposta não é JSON válido")

            else:
                print(f"\n❌ Erro {response.status_code}: {response.text}")

        except Exception as e:
            print(f"\n❌ Erro na chamada API: {e}")

    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60)
    print("\n📊 Próximos passos:")
    print("   1. Se detectou kills: OCR e Vision API estão OK!")
    print("   2. Se não detectou: problema no ROI ou imagem")
    print("   3. Ajuste ROI no .env se necessário")
    print()

if __name__ == "__main__":
    asyncio.run(test_single_frame())
