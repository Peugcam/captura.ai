"""
LiteLLM Client for Vision API with intelligent fallback routing
Fallback chain: Llama-3.2-Vision → Qwen2-VL → OpenRouter → GPT-4o
"""

import base64
import logging
import time
from typing import Dict, List, Optional

import litellm
from litellm import acompletion, completion_cost

logger = logging.getLogger(__name__)

# Suppress LiteLLM debug logs
litellm.set_verbose = False


class LiteLLMVisionClient:
    """
    Multi-model Vision API client with automatic fallback
    Cost-optimized routing: cheaper models first, GPT-4o as last resort
    """

    def __init__(self, api_keys: Dict[str, str], enable_fallback: bool = True):
        """
        Initialize LiteLLM client

        Args:
            api_keys: Dictionary of API keys
                {
                    "together": "...",
                    "siliconflow": "...",
                    "openrouter": "...",
                    "openai": "..."
                }
            enable_fallback: Enable automatic fallback on errors
        """
        self.api_keys = api_keys
        self.enable_fallback = enable_fallback

        # Fallback chain (cheap to expensive)
        self.model_chain = []

        # Together AI - Llama 3.2 Vision (fastest, cheapest)
        if api_keys.get("together"):
            self.model_chain.append({
                "provider": "together_ai",
                "model": "together_ai/meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
                "api_key": api_keys["together"],
                "cost_per_1k_tokens": 0.0003,  # $0.30 per 1M tokens (approx)
                "timeout": 30,
            })

        # SiliconFlow - Qwen2-VL (good quality, low cost)
        if api_keys.get("siliconflow"):
            self.model_chain.append({
                "provider": "siliconflow",
                "model": "siliconflow/Qwen/Qwen2-VL-7B-Instruct",
                "api_key": api_keys["siliconflow"],
                "cost_per_1k_tokens": 0.0004,  # $0.40 per 1M tokens (approx)
                "timeout": 30,
            })

        # OpenRouter - Multiple models available as fallback
        if api_keys.get("openrouter"):
            self.model_chain.append({
                "provider": "openrouter",
                "model": "openrouter/openai/gpt-4o",  # OpenRouter routes to GPT-4o
                "api_key": api_keys["openrouter"],
                "cost_per_1k_tokens": 0.002,  # $2.00 per 1M tokens (approx)
                "timeout": 30,
            })

        # OpenAI GPT-4o - Highest quality, highest cost (last resort)
        if api_keys.get("openai"):
            self.model_chain.append({
                "provider": "openai",
                "model": "gpt-4o",
                "api_key": api_keys["openai"],
                "cost_per_1k_tokens": 0.0025,  # $2.50 per 1M input tokens
                "timeout": 30,
            })

        if not self.model_chain:
            raise ValueError("No API keys provided. At least one provider is required.")

        logger.info(f"LiteLLM initialized with {len(self.model_chain)} models in fallback chain")
        for i, model in enumerate(self.model_chain, 1):
            logger.info(f"  {i}. {model['provider']}: {model['model']} (${model['cost_per_1k_tokens']:.4f}/1k tokens)")

        # Stats tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "model_usage": {model["provider"]: 0 for model in self.model_chain},
        }

    async def vision_chat_multiple(
        self,
        model: str,  # Ignored - we use fallback chain instead
        prompt: str,
        images_base64: List[str],
        temperature: float = 0,
        max_tokens: int = 2000,
        force_model: Optional[str] = None,
    ) -> Dict:
        """
        Send vision chat request with automatic fallback

        Args:
            model: Ignored (kept for backward compatibility)
            prompt: Text prompt for vision analysis
            images_base64: List of base64-encoded images
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens
            force_model: Force specific model (skip fallback chain)

        Returns:
            {
                "success": bool,
                "content": str (if success),
                "error": str (if failure),
                "model_used": str,
                "usage": dict,
                "cost": float
            }
        """
        self.stats["total_requests"] += 1

        # Build messages with image URLs
        content = [{"type": "text", "text": prompt}]

        for img_b64 in images_base64:
            # LiteLLM supports data URLs
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })

        messages = [{"role": "user", "content": content}]

        # If force_model specified, use it directly
        if force_model:
            model_config = next((m for m in self.model_chain if m["model"] == force_model), None)
            if model_config:
                return await self._call_model(model_config, messages, temperature, max_tokens)
            else:
                logger.error(f"Forced model {force_model} not found in chain")
                return {
                    "success": False,
                    "error": f"Model {force_model} not available",
                }

        # Try each model in fallback chain
        last_error = None

        for model_config in self.model_chain:
            try:
                result = await self._call_model(model_config, messages, temperature, max_tokens)

                if result["success"]:
                    self.stats["successful_requests"] += 1
                    self.stats["model_usage"][model_config["provider"]] += 1
                    self.stats["total_cost"] += result.get("cost", 0.0)
                    return result

                # If specific model failed, try next one
                last_error = result.get("error", "Unknown error")
                logger.warning(
                    f"Model {model_config['provider']} failed: {last_error}, "
                    f"trying next in chain..."
                )

                if not self.enable_fallback:
                    break  # Don't fallback if disabled

            except Exception as e:
                last_error = str(e)
                logger.error(f"Exception calling {model_config['provider']}: {e}")

                if not self.enable_fallback:
                    break

        # All models failed
        self.stats["failed_requests"] += 1
        return {
            "success": False,
            "error": f"All models failed. Last error: {last_error}",
        }

    async def _call_model(
        self,
        model_config: Dict,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
    ) -> Dict:
        """
        Call a specific model via LiteLLM

        Args:
            model_config: Model configuration dict
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            Result dictionary
        """
        provider = model_config["provider"]
        model = model_config["model"]
        api_key = model_config["api_key"]
        timeout = model_config["timeout"]

        logger.debug(f"Calling {provider} ({model})...")
        start_time = time.time()

        try:
            response = await acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                api_key=api_key,
            )

            elapsed = time.time() - start_time

            # Extract response
            content = response.choices[0].message.content

            # Calculate cost
            usage = response.usage
            input_tokens = usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else 0
            output_tokens = usage.completion_tokens if hasattr(usage, 'completion_tokens') else 0

            # Estimate cost (litellm.completion_cost sometimes doesn't work for all providers)
            try:
                cost = completion_cost(completion_response=response)
            except Exception:
                # Fallback cost estimation
                cost = (input_tokens + output_tokens) / 1000 * model_config["cost_per_1k_tokens"]

            logger.info(
                f"✓ {provider} succeeded in {elapsed:.2f}s "
                f"({input_tokens}+{output_tokens} tokens, ${cost:.4f})"
            )

            return {
                "success": True,
                "content": content,
                "model_used": f"{provider}/{model}",
                "usage": {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                },
                "cost": cost,
                "latency": elapsed,
            }

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"✗ {provider} failed after {elapsed:.2f}s: {e}")

            return {
                "success": False,
                "error": str(e),
                "model_used": f"{provider}/{model}",
            }

    def get_stats(self) -> Dict:
        """Get client statistics"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "model_usage": {model["provider"]: 0 for model in self.model_chain},
        }
        logger.info("Stats reset")
