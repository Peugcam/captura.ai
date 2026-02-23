"""
Unit Tests: LiteLLM Vision Client
==================================

Tests the LiteLLM multi-provider vision client initialization and configuration.
Note: These tests focus on the initialization logic without making actual API calls.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

# Mock litellm globally before import
sys.modules['litellm'] = MagicMock()

from src.litellm_client import LiteLLMVisionClient


@pytest.fixture
def api_keys():
    """Sample API keys for all providers"""
    return {
        "together": "test-together-key",
        "siliconflow": "test-siliconflow-key",
        "openrouter": "test-openrouter-key",
        "openai": "test-openai-key"
    }


@pytest.fixture
def minimal_api_keys():
    """Minimal API keys (one provider)"""
    return {"openai": "test-openai-key"}


class TestLiteLLMClientInit:
    """Test client initialization"""

    def test_init_all_providers(self, api_keys):
        """Test initialization with all providers"""
        client = LiteLLMVisionClient(api_keys)
        assert len(client.model_chain) == 4
        assert client.enable_fallback is True

    def test_init_single_provider(self, minimal_api_keys):
        """Test initialization with single provider"""
        client = LiteLLMVisionClient(minimal_api_keys)
        assert len(client.model_chain) == 1
        assert client.model_chain[0]["provider"] == "openai"

    def test_init_fallback_disabled(self, api_keys):
        """Test initialization with fallback disabled"""
        client = LiteLLMVisionClient(api_keys, enable_fallback=False)
        assert client.enable_fallback is False

    def test_init_no_api_keys_raises_error(self):
        """Test initialization with no API keys raises ValueError"""
        with pytest.raises(ValueError, match="No API keys provided"):
            LiteLLMVisionClient({})

    def test_model_chain_order(self, api_keys):
        """Test that model chain is ordered by cost"""
        client = LiteLLMVisionClient(api_keys)
        providers = [m["provider"] for m in client.model_chain]
        assert providers == ["together_ai", "siliconflow", "openrouter", "openai"]

    def test_partial_api_keys(self):
        """Test initialization with partial API keys"""
        partial_keys = {"together": "test-key", "openai": "test-key"}
        client = LiteLLMVisionClient(partial_keys)
        assert len(client.model_chain) == 2


class TestStatistics:
    """Test statistics tracking"""

    def test_get_stats_returns_copy(self, api_keys):
        """Test get_stats returns a copy of stats"""
        client = LiteLLMVisionClient(api_keys)
        stats1 = client.get_stats()
        stats2 = client.get_stats()
        assert stats1 == stats2
        assert stats1 is not stats2

    def test_reset_stats(self, api_keys):
        """Test stats reset"""
        client = LiteLLMVisionClient(api_keys)
        client.stats["total_requests"] = 10
        client.stats["total_cost"] = 5.0
        client.reset_stats()
        assert client.stats["total_requests"] == 0
        assert client.stats["total_cost"] == 0.0

    def test_stats_initialized(self, api_keys):
        """Test that statistics are properly initialized"""
        client = LiteLLMVisionClient(api_keys)
        assert "total_requests" in client.stats
        assert "successful_requests" in client.stats
        assert "failed_requests" in client.stats
        assert "total_cost" in client.stats


class TestModelConfiguration:
    """Test model configuration and costs"""

    def test_together_ai_config(self, api_keys):
        """Test Together AI model configuration"""
        client = LiteLLMVisionClient(api_keys)
        together_model = client.model_chain[0]
        assert together_model["provider"] == "together_ai"
        assert together_model["cost_per_1k_tokens"] == 0.0003

    def test_openai_config(self, api_keys):
        """Test OpenAI GPT-4o configuration"""
        client = LiteLLMVisionClient(api_keys)
        openai_model = client.model_chain[3]
        assert openai_model["provider"] == "openai"
        assert openai_model["model"] == "gpt-4o"
        assert openai_model["cost_per_1k_tokens"] == 0.0025


class TestCostOptimization:
    """Test cost-optimized routing"""

    def test_models_ordered_by_cost(self, api_keys):
        """Test that models are ordered from cheapest to most expensive"""
        client = LiteLLMVisionClient(api_keys)
        costs = [m["cost_per_1k_tokens"] for m in client.model_chain]
        assert costs == sorted(costs)

    def test_cheapest_model_first(self, api_keys):
        """Test that cheapest model is tried first"""
        client = LiteLLMVisionClient(api_keys)
        first_model = client.model_chain[0]
        assert first_model["provider"] == "together_ai"
        assert first_model["cost_per_1k_tokens"] == 0.0003

    def test_gpt4o_last_resort(self, api_keys):
        """Test that GPT-4o is last (most expensive)"""
        client = LiteLLMVisionClient(api_keys)
        last_model = client.model_chain[-1]
        assert last_model["provider"] == "openai"
        assert last_model["model"] == "gpt-4o"


class TestAPIKeyManagement:
    """Test API key storage and access"""

    def test_api_keys_stored(self, api_keys):
        """Test that API keys are stored correctly"""
        client = LiteLLMVisionClient(api_keys)
        assert client.api_keys == api_keys

    def test_api_keys_assigned_to_models(self, api_keys):
        """Test that API keys are assigned to respective models"""
        client = LiteLLMVisionClient(api_keys)
        for model in client.model_chain:
            assert "api_key" in model
            assert model["api_key"] is not None


class TestFallbackConfiguration:
    """Test fallback settings"""

    def test_fallback_enabled_by_default(self, api_keys):
        """Test that fallback is enabled by default"""
        client = LiteLLMVisionClient(api_keys)
        assert client.enable_fallback is True

    def test_can_disable_fallback(self, api_keys):
        """Test that fallback can be disabled"""
        client = LiteLLMVisionClient(api_keys, enable_fallback=False)
        assert client.enable_fallback is False


class TestModelChainBuilding:
    """Test model chain construction"""

    def test_only_provided_keys_in_chain(self):
        """Test that only models with provided keys are in chain"""
        keys = {"together": "key1", "openai": "key2"}
        client = LiteLLMVisionClient(keys)
        providers = [m["provider"] for m in client.model_chain]
        assert "together_ai" in providers
        assert "openai" in providers
        assert "siliconflow" not in providers

    def test_empty_model_chain_raises_error(self):
        """Test that empty model chain raises error"""
        with pytest.raises(ValueError, match="No API keys provided"):
            LiteLLMVisionClient({})


class TestIntegrationScenarios:
    """Test realistic usage scenarios"""

    def test_multi_provider_setup(self, api_keys):
        """Test setting up client with multiple providers"""
        client = LiteLLMVisionClient(api_keys)
        assert len(client.model_chain) == 4
        costs = [m["cost_per_1k_tokens"] for m in client.model_chain]
        assert costs == [0.0003, 0.0004, 0.002, 0.0025]

    def test_budget_conscious_setup(self):
        """Test setup for budget-conscious usage (cheap models only)"""
        budget_keys = {"together": "key1", "siliconflow": "key2"}
        client = LiteLLMVisionClient(budget_keys)
        assert len(client.model_chain) == 2
        max_cost = max(m["cost_per_1k_tokens"] for m in client.model_chain)
        assert max_cost <= 0.0004

    def test_premium_only_setup(self):
        """Test setup with only premium model"""
        premium_keys = {"openai": "key"}
        client = LiteLLMVisionClient(premium_keys)
        assert len(client.model_chain) == 1
        assert client.model_chain[0]["provider"] == "openai"
        assert client.model_chain[0]["model"] == "gpt-4o"


class TestVisionChatMultipleMethod:
    """Test vision_chat_multiple method logic"""

    @pytest.mark.asyncio
    async def test_vision_chat_increments_total_requests(self, api_keys):
        """Test that calling vision_chat_multiple increments total_requests"""
        client = LiteLLMVisionClient(api_keys)
        initial_requests = client.stats["total_requests"]

        # Mock acompletion to avoid actual API call
        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response):
            with patch('src.litellm_client.completion_cost', return_value=0.001):
                result = await client.vision_chat_multiple(
                    model="gpt-4o",
                    prompt="test prompt",
                    images_base64=["base64image"]
                )

        assert client.stats["total_requests"] == initial_requests + 1

    @pytest.mark.asyncio
    async def test_vision_chat_builds_messages_correctly(self, api_keys):
        """Test that vision_chat_multiple builds message structure correctly"""
        client = LiteLLMVisionClient(api_keys)

        # Mock acompletion to capture the messages parameter
        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50

        captured_messages = None

        async def capture_messages(*args, **kwargs):
            nonlocal captured_messages
            captured_messages = kwargs.get('messages')
            return mock_response

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, side_effect=capture_messages):
            with patch('src.litellm_client.completion_cost', return_value=0.001):
                await client.vision_chat_multiple(
                    model="gpt-4o",
                    prompt="analyze this",
                    images_base64=["img1", "img2"]
                )

        # Verify message structure
        assert captured_messages is not None
        assert len(captured_messages) == 1
        assert captured_messages[0]["role"] == "user"
        content = captured_messages[0]["content"]
        assert isinstance(content, list)
        assert len(content) == 3  # 1 text + 2 images

    @pytest.mark.asyncio
    async def test_vision_chat_force_model(self, api_keys):
        """Test forcing a specific model"""
        client = LiteLLMVisionClient(api_keys)

        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Forced model response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response) as mock_call:
            with patch('src.litellm_client.completion_cost', return_value=0.001):
                result = await client.vision_chat_multiple(
                    model="ignored",
                    prompt="test",
                    images_base64=["img"],
                    force_model="gpt-4o"
                )

        # Verify the correct model was called
        assert mock_call.called
        call_kwargs = mock_call.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_vision_chat_fallback_disabled(self, api_keys):
        """Test behavior when fallback is disabled"""
        client = LiteLLMVisionClient(api_keys, enable_fallback=False)

        from unittest.mock import AsyncMock, patch

        # Make the first model fail
        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, side_effect=Exception("API Error")):
            result = await client.vision_chat_multiple(
                model="gpt-4o",
                prompt="test",
                images_base64=["img"]
            )

        # Should fail without trying other models
        assert result["success"] is False
        assert client.stats["failed_requests"] == 1

    @pytest.mark.asyncio
    async def test_vision_chat_successful_response(self, api_keys):
        """Test successful API response handling"""
        client = LiteLLMVisionClient(api_keys)

        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Successfully analyzed image"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 250
        mock_response.usage.completion_tokens = 100

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response):
            with patch('src.litellm_client.completion_cost', return_value=0.005):
                result = await client.vision_chat_multiple(
                    model="gpt-4o",
                    prompt="analyze",
                    images_base64=["img"]
                )

        assert result["success"] is True
        assert result["content"] == "Successfully analyzed image"
        assert client.stats["successful_requests"] == 1

    @pytest.mark.asyncio
    async def test_vision_chat_updates_cost_stats(self, api_keys):
        """Test that cost statistics are updated correctly"""
        client = LiteLLMVisionClient(api_keys)
        initial_cost = client.stats["total_cost"]

        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response):
            with patch('src.litellm_client.completion_cost', return_value=0.123):
                await client.vision_chat_multiple(
                    model="gpt-4o",
                    prompt="test",
                    images_base64=["img"]
                )

        assert client.stats["total_cost"] > initial_cost
        assert client.stats["total_cost"] == initial_cost + 0.123

    @pytest.mark.asyncio
    async def test_vision_chat_invalid_force_model(self, api_keys):
        """Test forcing a model that doesn't exist"""
        client = LiteLLMVisionClient(api_keys)

        result = await client.vision_chat_multiple(
            model="ignored",
            prompt="test",
            images_base64=["img"],
            force_model="nonexistent-model"
        )

        assert result["success"] is False
        assert "not available" in result["error"]

    @pytest.mark.asyncio
    async def test_vision_chat_exception_in_call_model(self, api_keys):
        """Test exception handling during _call_model execution"""
        client = LiteLLMVisionClient(api_keys, enable_fallback=True)

        from unittest.mock import AsyncMock, patch

        # Simulate an exception raised from within the try block
        call_count = 0

        async def mock_call_model(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # First call raises exception (line 181-183)
            if call_count == 1:
                raise Exception("Network timeout")
            # Second call succeeds
            return {
                "success": True,
                "content": "Fallback worked",
                "model_used": "fallback/model",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                "cost": 0.001
            }

        with patch.object(client, '_call_model', side_effect=mock_call_model):
            result = await client.vision_chat_multiple(
                model="gpt-4o",
                prompt="test",
                images_base64=["img"]
            )

        # Should succeed with fallback
        assert result["success"] is True
        assert result["content"] == "Fallback worked"
        assert call_count == 2  # First failed, second succeeded


class TestCallModelMethod:
    """Test _call_model internal method"""

    @pytest.mark.asyncio
    async def test_call_model_success(self, api_keys):
        """Test successful model call"""
        client = LiteLLMVisionClient(api_keys)
        model_config = client.model_chain[0]
        messages = [{"role": "user", "content": "test"}]

        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Model response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response):
            with patch('src.litellm_client.completion_cost', return_value=0.001):
                result = await client._call_model(
                    model_config=model_config,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )

        assert result["success"] is True
        assert result["content"] == "Model response"
        assert "usage" in result
        assert result["usage"]["prompt_tokens"] == 10
        assert result["usage"]["completion_tokens"] == 20

    @pytest.mark.asyncio
    async def test_call_model_failure(self, api_keys):
        """Test model call failure handling"""
        client = LiteLLMVisionClient(api_keys)
        model_config = client.model_chain[0]
        messages = [{"role": "user", "content": "test"}]

        from unittest.mock import AsyncMock, patch

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, side_effect=Exception("API timeout")):
            result = await client._call_model(
                model_config=model_config,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

        assert result["success"] is False
        assert "API timeout" in result["error"]

    @pytest.mark.asyncio
    async def test_call_model_cost_calculation_fallback(self, api_keys):
        """Test cost calculation when completion_cost fails"""
        client = LiteLLMVisionClient(api_keys)
        model_config = client.model_chain[0]
        messages = [{"role": "user", "content": "test"}]

        from unittest.mock import AsyncMock, patch
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 1000
        mock_response.usage.completion_tokens = 1000

        with patch('src.litellm_client.acompletion', new_callable=AsyncMock, return_value=mock_response):
            # Make completion_cost raise an exception to trigger fallback
            with patch('src.litellm_client.completion_cost', side_effect=Exception("Cost calc failed")):
                result = await client._call_model(
                    model_config=model_config,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )

        assert result["success"] is True
        # Should use fallback cost calculation
        assert "cost" in result
        # Verify cost was calculated using fallback formula
        expected_cost = 2000 / 1000 * model_config["cost_per_1k_tokens"]
        assert result["cost"] == expected_cost

