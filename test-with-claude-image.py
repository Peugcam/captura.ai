#!/usr/bin/env python3
"""Test with the image user sent to Claude"""

import base64
import asyncio
import httpx
from PIL import Image
import io

# The image data will be saved by Claude
# This is a simplified test using the screenshot provided

async def test_detection():
    print("\n" + "="*60)
    print("TESTE DE DETECCAO - IMAGEM DO USUARIO")
    print("="*60)

    # For now, let's capture current screen
    print("\nCapturando screenshot atual...")
    print("(Mantenha a imagem do GTA visivel na tela)")
    input("Pressione ENTER para capturar...")

    from PIL import ImageGrab
    screenshot = ImageGrab.grab()

    # Extract ROI (top-right where kill feed is)
    width, height = screenshot.size
    roi_x = int(width * 0.75)
    roi_y = 0
    roi_width = int(width * 0.25)
    roi_height = int(height * 0.35)

    roi = screenshot.crop((roi_x, roi_y, roi_x + roi_width, roi_y + roi_height))
    roi.save("test_killfeed_roi.png")

    print(f"\nResolucao: {width}x{height}")
    print(f"ROI: {roi_width}x{roi_height}")
    print(f"ROI salvo em: test_killfeed_roi.png")

    # Encode to base64
    buffer = io.BytesIO()
    roi.save(buffer, format="PNG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"Tamanho: {len(buffer.getvalue()) / 1024:.1f} KB")

    # Test OCR
    print("\nTestando OCR...")
    try:
        import pytesseract
        text = pytesseract.image_to_string(roi, config='--psm 6')
        print(f"Texto OCR ({len(text)} chars):")
        print(text[:300])

        if "MTL" in text or "ibra" in text or "killed" in text.lower():
            print("OK: OCR detectou texto relevante!")
        else:
            print("AVISO: OCR nao detectou kills esperadas")
    except Exception as e:
        print(f"Erro OCR: {e}")

    # Call Vision API
    print("\nChamando GPT-4o Vision API...")
    print("Custo: ~$0.002\n")

    import os

    # Use environment variable for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("ERROR: Set OPENROUTER_API_KEY environment variable")
        return

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
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
                                    "text": """This is a GTA Battle Royale kill feed from top-right corner.

Extract ALL kill events. Each kill shows: [TEAM] killer [ICON] victim [DISTANCE]

For each kill:
- killer: player name who killed
- victim: player who died
- distance: meters shown (e.g. "128m")

Return ONLY JSON array:
[{"killer": "MTL", "victim": "ibra7b", "distance": "128m"}]

If no kills visible, return: []"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_b64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                print("="*60)
                print("RESPOSTA GPT-4o:")
                print("="*60)
                print(content)
                print("="*60)

                # Parse JSON
                import json
                try:
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()

                    kills = json.loads(content)

                    if kills:
                        print(f"\nSUCESSO! {len(kills)} KILLS DETECTADAS:\n")
                        for i, k in enumerate(kills, 1):
                            print(f"  Kill #{i}:")
                            print(f"    {k.get('killer', '?')} matou {k.get('victim', '?')}")
                            print(f"    Distancia: {k.get('distance', 'N/A')}")
                    else:
                        print("\nNenhuma kill detectada")

                except Exception as e:
                    print(f"\nErro ao parsear JSON: {e}")
                    print("Mas a API respondeu (veja acima)")

            else:
                print(f"Erro {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("TESTE CONCLUIDO")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_detection())
