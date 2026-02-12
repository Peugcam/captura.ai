"""
Gemini Flash 2.0 Client - NASA-Level Cost Optimization
=======================================================

90% cheaper than GPT-4o with similar performance for kill feed detection.
Supports fallback when GPT-4o fails or is slow.

Pricing comparison (per 1M tokens):
- GPT-4o: $2.50 input / $10.00 output
- Gemini Flash 2.0: $0.075 input / $0.30 output
- Savings: 97% input / 97% output

Author: Paulo Eugenio Campos
"""

import base64
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Cliente para Google Gemini Flash 2.0 Vision API.

    Suporta:
    - Vision analysis (kill feed detection)
    - Multiple image processing
    - Structured JSON output
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Inicializa cliente Gemini.

        Args:
            api_key: Google AI Studio API key
            model: Modelo Gemini (default: gemini-2.0-flash-exp)
        """
        if not api_key or not api_key.strip():
            raise ValueError("Gemini API key is required")

        self.api_key = api_key.strip()
        self.model = model
        self.api_base = "https://generativelanguage.googleapis.com/v1beta/models"

        logger.info(f"🤖 Gemini client initialized (model: {model})")

    def vision_chat(
        self,
        prompt: str,
        image_base64: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Processa uma imagem com Gemini Vision.

        Args:
            prompt: Pergunta/instrução
            image_base64: Imagem em base64
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens na resposta

        Returns:
            Dict com success, content, error
        """
        try:
            url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"

            # Preparar payload
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }

            # Fazer request
            response = requests.post(
                url,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

            data = response.json()

            # Extrair conteúdo da resposta
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    return {"success": True, "content": text}

            logger.error(f"Gemini: Unexpected response format: {data}")
            return {"success": False, "error": "Unexpected response format"}

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {"success": False, "error": str(e)}

    def vision_chat_multiple(
        self,
        prompt: str,
        images_base64: List[str],
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Processa múltiplas imagens com Gemini Vision.

        Args:
            prompt: Pergunta/instrução
            images_base64: Lista de imagens em base64
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens na resposta

        Returns:
            Dict com success, content, error
        """
        try:
            url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"

            # Preparar partes (texto + todas as imagens)
            parts = [{"text": prompt}]

            for img_b64 in images_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }
                })

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }

            # Fazer request
            response = requests.post(
                url,
                json=payload,
                timeout=60,  # Mais tempo para múltiplas imagens
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

            data = response.json()

            # Extrair conteúdo da resposta
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    return {"success": True, "content": text}

            logger.error(f"Gemini: Unexpected response format: {data}")
            return {"success": False, "error": "Unexpected response format"}

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {"success": False, "error": str(e)}
