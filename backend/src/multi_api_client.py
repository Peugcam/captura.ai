"""
Multi-API Client - Load Balancing entre OpenRouter e OpenAI
Suporta rotação automática de chaves para melhor throughput
"""

import requests
import logging
from typing import Dict, Any, List
from itertools import cycle

logger = logging.getLogger(__name__)


class MultiAPIClient:
    """Cliente com balanceamento de carga entre múltiplas API keys"""

    def __init__(self, api_keys: List[str]):
        """
        Args:
            api_keys: Lista de chaves API (OpenRouter ou OpenAI)
        """
        if not api_keys:
            raise ValueError("Pelo menos uma API key é necessária")

        self.clients = []

        for key in api_keys:
            key = key.strip()
            if not key:
                continue

            # Detectar tipo de chave
            if key.startswith("sk-or-"):
                # OpenRouter key
                self.clients.append({
                    "type": "openrouter",
                    "api_key": key,
                    "api_base": "https://openrouter.ai/api/v1",
                    "model_prefix": ""  # OpenRouter usa formato completo: openai/gpt-4o
                })
                logger.info(f"✅ OpenRouter key added: ...{key[-8:]}")
            else:
                # OpenAI direct key
                self.clients.append({
                    "type": "openai",
                    "api_key": key,
                    "api_base": "https://api.openai.com/v1",
                    "model_prefix": ""  # OpenAI usa: gpt-4o (sem prefixo)
                })
                logger.info(f"✅ OpenAI key added: ...{key[-8:]}")

        if not self.clients:
            raise ValueError("Nenhuma API key válida encontrada")

        # Criar iterador circular para rotação round-robin
        self.client_cycle = cycle(self.clients)
        self.current_client = next(self.client_cycle)

        logger.info(f"🔄 Multi-API Client initialized with {len(self.clients)} keys")

    def _get_next_client(self) -> Dict[str, str]:
        """Rotaciona para próxima chave (round-robin)"""
        self.current_client = next(self.client_cycle)
        return self.current_client

    def _normalize_model(self, model: str, client_type: str) -> str:
        """
        Normaliza nome do modelo baseado no tipo de cliente

        Args:
            model: Nome do modelo (ex: "openai/gpt-4o")
            client_type: "openrouter" ou "openai"

        Returns:
            Modelo normalizado
        """
        if client_type == "openai":
            # OpenAI não usa prefixo "openai/"
            if model.startswith("openai/"):
                return model.replace("openai/", "")
            return model
        else:
            # OpenRouter usa prefixo completo
            return model

    def chat_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 500,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Chama chat completion com rotação automática de chaves

        Args:
            model: Nome do modelo
            messages: Lista de mensagens
            temperature: Temperatura
            max_tokens: Max tokens
            timeout: Timeout em segundos

        Returns:
            Dict com resultado
        """
        # Tentar com cliente atual
        client = self.current_client
        result = self._call_api(client, model, messages, temperature, max_tokens, timeout)

        # Se falhar, tentar próxima chave (se houver mais de uma)
        if not result["success"] and len(self.clients) > 1:
            logger.warning(f"⚠️ Retrying with next API key...")
            client = self._get_next_client()
            result = self._call_api(client, model, messages, temperature, max_tokens, timeout)

        # Rotacionar para próxima chamada
        if len(self.clients) > 1:
            self._get_next_client()

        return result

    def _call_api(
        self,
        client: Dict[str, str],
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """Faz chamada à API específica"""

        normalized_model = self._normalize_model(model, client["type"])

        headers = {
            "Authorization": f"Bearer {client['api_key']}",
            "Content-Type": "application/json"
        }

        # Headers adicionais para OpenRouter
        if client["type"] == "openrouter":
            headers["HTTP-Referer"] = "http://localhost:8000"
            headers["X-Title"] = "Naruto Combat Analyzer"

        payload = {
            "model": normalized_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            logger.debug(f"📡 Calling {client['type']} API with model {normalized_model}")

            response = requests.post(
                f"{client['api_base']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout
            )

            response.raise_for_status()
            data = response.json()

            # Extrair resposta
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {})

            logger.debug(f"✅ {client['type']} API success")

            return {
                "success": True,
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get('prompt_tokens', 0),
                    "completion_tokens": usage.get('completion_tokens', 0),
                    "total_tokens": usage.get('total_tokens', 0)
                },
                "model": data.get('model', normalized_model),
                "api_type": client["type"]
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {client['type']} API error: {e}")
            return {
                "success": False,
                "content": "",
                "usage": {},
                "model": normalized_model,
                "error": str(e),
                "api_type": client["type"]
            }

    def vision_chat_multiple(
        self,
        model: str,
        prompt: str,
        images_base64: list,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Chama vision model com múltiplas imagens

        Args:
            model: Nome do modelo
            prompt: Prompt de texto
            images_base64: Lista de imagens em base64
            temperature: Temperatura
            max_tokens: Max tokens

        Returns:
            Dict com resultado
        """
        # Build content array
        content = [{"type": "text", "text": prompt}]

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

        # Timeout adaptativo
        num_images = len(images_base64)
        adaptive_timeout = min(10 + (num_images * 2), 30)

        logger.info(f"📸 Sending {num_images} images to {model}")

        return self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=adaptive_timeout
        )
