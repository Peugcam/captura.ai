"""
Teste de API Keys - Verifica se as chaves estão funcionando
"""
import requests
import json
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

def test_openai():
    """Testa chave OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada")
        return False

    print(f"🔑 Testing OpenAI key: {api_key[:15]}...{api_key[-8:]}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",  # Modelo mais barato para teste
        "messages": [
            {"role": "user", "content": "Say 'API working!' in one word"}
        ],
        "max_tokens": 10
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ OpenAI funcionando! Resposta: {content}")
            return True
        else:
            print(f"❌ OpenAI error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ OpenAI exception: {e}")
        return False


def test_openrouter():
    """Testa chave OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    if not api_key:
        print("❌ OPENROUTER_API_KEY não encontrada")
        return False

    print(f"\n🔑 Testing OpenRouter key: {api_key[:15]}...{api_key[-8:]}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "GTA Analytics Test"
    }

    payload = {
        "model": "google/gemini-flash-1.5-8b",  # Modelo gratuito
        "messages": [
            {"role": "user", "content": "Say 'API working!' in one word"}
        ],
        "max_tokens": 10
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ OpenRouter funcionando! Resposta: {content}")
            return True
        else:
            print(f"❌ OpenRouter error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ OpenRouter exception: {e}")
        return False


def test_vision_api():
    """Testa chamada de visão com uma imagem simples"""
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    if not api_key:
        print("\n⚠️ Pulando teste de visão (sem OpenRouter key)")
        return False

    print(f"\n🖼️ Testing Vision API with image...")

    # Imagem de teste pequena (1x1 pixel branco em base64)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "GTA Analytics Test"
    }

    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What color is this image? Answer in one word."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{test_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 20
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ Vision API funcionando! Resposta: {content}")
            return True
        else:
            print(f"❌ Vision API error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Vision API exception: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🧪 GTA ANALYTICS - API KEYS TEST")
    print("="*60)

    results = {
        "OpenAI": test_openai(),
        "OpenRouter": test_openrouter(),
        "Vision": test_vision_api()
    }

    print("\n" + "="*60)
    print("📊 RESULTADOS:")
    print("="*60)
    for api, success in results.items():
        status = "✅ OK" if success else "❌ FALHOU"
        print(f"{api:20} {status}")

    print("="*60)

    # Diagnóstico
    if not any(results.values()):
        print("\n⚠️ PROBLEMA CRÍTICO: Nenhuma API está funcionando!")
        print("\n📝 Verifique:")
        print("   1. Se as chaves no .env estão corretas")
        print("   2. Se as chaves têm créditos disponíveis")
        print("   3. Se não estão expiradas")
        print("\n💡 Acesse https://platform.openai.com/api-keys")
        print("💡 Acesse https://openrouter.ai/keys")
    elif not results["Vision"]:
        print("\n⚠️ A API de texto funciona, mas a Vision API falhou!")
        print("   Isso explica por que os frames não estão sendo processados.")
