#!/usr/bin/env python3
"""Test detection with user-provided screenshot"""

import base64
import asyncio
import httpx
from pathlib import Path

async def test_screenshot():
    print("\n" + "="*60)
    print("TESTE DE DETECCAO - SCREENSHOT DO USUARIO")
    print("="*60)

    # Read the screenshot image you sent
    image_path = input("\nDigite o caminho completo da imagem PNG: ")

    if not Path(image_path).exists():
        print(f"Erro: Arquivo nao encontrado: {image_path}")
        return

    print(f"\nLendo imagem: {image_path}")

    with open(image_path, "rb") as f:
        image_data = f.read()

    image_base64 = base64.b64encode(image_data).decode()
    print(f"Tamanho: {len(image_data) / 1024:.1f} KB")

    # Extract ROI (top-right 25% width, top 35% height)
    from PIL import Image
    import io

    img = Image.open(image_path)
    width, height = img.size

    roi_x = int(width * 0.75)
    roi_y = 0
    roi_width = int(width * 0.25)
    roi_height = int(height * 0.35)

    roi_img = img.crop((roi_x, roi_y, roi_x + roi_width, roi_y + roi_height))
    roi_img.save("test_roi_extracted.png")

    print(f"\nResolucao original: {width}x{height}")
    print(f"ROI extraido: {roi_width}x{roi_height}")
    print(f"ROI salvo em: test_roi_extracted.png")

    # Encode ROI
    buffer = io.BytesIO()
    roi_img.save(buffer, format="PNG")
    roi_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Test OCR
    print("\nTestando OCR no ROI...")
    try:
        import pytesseract
        ocr_text = pytesseract.image_to_string(roi_img, config='--psm 6')
        print(f"Texto detectado:\n{ocr_text}")

        keywords = ["killed", "kill", "matou", "MTL", "ibra", "manetzz"]
        found = [kw for kw in keywords if kw in ocr_text]
        print(f"\nPalavras-chave encontradas: {found}")
    except Exception as e:
        print(f"Erro OCR: {e}")

    # Call Vision API
    print("\nChamando Vision API (GPT-4o via OpenRouter)...")
    print("Custo estimado: ~$0.002")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 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",
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
                                    "text": """Analyze this GTA Battle Royale kill feed (canto superior direito).

Extract ALL kill events visible. For each kill event, identify:
- killer: nome do jogador que matou (ex: "MTL", "PPP")
- victim: nome do jogador que morreu (ex: "ibra7b", "pikachu1337")
- distance: distancia em metros se mostrado (ex: "128m", "121m")

IGNORE weapon icons (caveira, cruz, etc) - we only need player names and distance.

Return ONLY valid JSON array:
[{"killer": "MTL", "victim": "ibra7b", "distance": "128m"}]

If NO kills visible, return: []"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{roi_base64}"
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

                print("\n" + "="*60)
                print("RESPOSTA DA VISION API:")
                print("="*60)
                print(content)
                print("="*60)

                # Try to parse JSON
                import json
                try:
                    # Extract JSON from response
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()

                    kills = json.loads(content)

                    if kills:
                        print(f"\nKILLS DETECTADAS: {len(kills)}")
                        for i, kill in enumerate(kills, 1):
                            print(f"\nKill #{i}:")
                            print(f"  Killer: {kill.get('killer', 'N/A')}")
                            print(f"  Victim: {kill.get('victim', 'N/A')}")
                            print(f"  Distance: {kill.get('distance', 'N/A')}")
                            print(f"  Weapon: {kill.get('weapon', 'N/A')}")
                    else:
                        print("\nNenhuma kill detectada")
                except Exception as e:
                    print(f"\nAviso: Nao foi possivel parsear JSON: {e}")
                    print("Mas a Vision API respondeu corretamente acima!")

            else:
                print(f"\nErro {response.status_code}: {response.text}")

        except Exception as e:
            print(f"\nErro na chamada API: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("TESTE CONCLUIDO")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_screenshot())
