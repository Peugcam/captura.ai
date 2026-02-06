"""
Simple OpenRouter Client - Direct API calls without LiteLLM
Bypasses LiteLLM memory issues
"""

import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SimpleOpenRouter:
    """Direct OpenRouter API client without LiteLLM dependencies"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_base = "https://openrouter.ai/api/v1"

    def chat_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Call OpenRouter chat completion API

        Args:
            model: Model name (e.g., "openai/gpt-4o")
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            Dict with content, usage, model
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Optional
            "X-Title": "GTA Kill Tracker"  # Optional
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            # Extract response
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {})

            return {
                "success": True,
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get('prompt_tokens', 0),
                    "completion_tokens": usage.get('completion_tokens', 0),
                    "total_tokens": usage.get('total_tokens', 0)
                },
                "model": data.get('model', model)
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            return {
                "success": False,
                "content": "",
                "usage": {},
                "model": model,
                "error": str(e)
            }

    def vision_chat(
        self,
        model: str,
        prompt: str,
        image_base64: str,
        temperature: float = 0.1,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Call vision model with image

        Args:
            model: Model name
            prompt: Text prompt
            image_base64: Base64-encoded image
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            Dict with content, usage, model
        """
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }]

        return self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def vision_chat_multiple(
        self,
        model: str,
        prompt: str,
        images_base64: list,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Call vision model with MULTIPLE images (batch processing)

        Args:
            model: Model name
            prompt: Text prompt
            images_base64: List of base64-encoded images
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            Dict with content, usage, model
        """
        # Build content array: text first, then all images
        content = [{"type": "text", "text": prompt}]

        # Add all images to the content
        for img_base64 in images_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                }
            })

        messages = [{
            "role": "user",
            "content": content
        }]

        logger.info(f"📸 Sending {len(images_base64)} images to {model}")

        return self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
