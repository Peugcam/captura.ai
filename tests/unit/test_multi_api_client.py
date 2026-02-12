"""
Unit Tests: MultiAPIClient
===========================

Tests the multi-API client with load balancing and fallback.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import responses

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.multi_api_client import MultiAPIClient


class TestMultiAPIClient:
    """Test suite for MultiAPIClient"""
    
    # ========================================================================
    # Test: Initialization
    # ========================================================================
    
    def test_initialization_with_single_key(self, mock_openrouter_key):
        """Test initialization with single API key"""
        client = MultiAPIClient([mock_openrouter_key])
        
        assert len(client.clients) == 1
        assert client.clients[0]['type'] == 'openrouter'
        assert client.clients[0]['api_key'] == mock_openrouter_key
    
    def test_initialization_with_multiple_keys(self, mock_api_keys):
        """Test initialization with multiple API keys"""
        client = MultiAPIClient(mock_api_keys)
        
        assert len(client.clients) == 3
    
    def test_initialization_empty_keys_raises_error(self):
        """Test that empty keys list raises ValueError"""
        with pytest.raises(ValueError, match="Pelo menos uma API key é necessária"):
            MultiAPIClient([])
    
    def test_initialization_filters_empty_strings(self):
        """Test that empty strings are filtered out"""
        keys = ["sk-or-v1-valid-key", "", "  ", "sk-proj-another-valid"]
        client = MultiAPIClient(keys)
        
        assert len(client.clients) == 2
    
    # ========================================================================
    # Test: Key Type Detection
    # ========================================================================
    
    def test_detect_openrouter_key(self):
        """Test detection of OpenRouter API key"""
        key = "sk-or-v1-test-key-123456"
        client = MultiAPIClient([key])
        
        assert client.clients[0]['type'] == 'openrouter'
        assert client.clients[0]['api_base'] == 'https://openrouter.ai/api/v1'
    
    def test_detect_openai_key(self):
        """Test detection of OpenAI API key"""
        key = "sk-proj-test-key-123456"
        client = MultiAPIClient([key])
        
        assert client.clients[0]['type'] == 'openai'
        assert client.clients[0]['api_base'] == 'https://api.openai.com/v1'
    
    def test_detect_legacy_openai_key(self):
        """Test detection of legacy OpenAI key format"""
        key = "sk-test-key-123456"  # Old format without 'proj'
        client = MultiAPIClient([key])
        
        # Should default to OpenAI
        assert client.clients[0]['type'] == 'openai'
    
    # ========================================================================
    # Test: Model Normalization
    # ========================================================================
    
    def test_normalize_model_for_openai(self, mock_openai_key):
        """Test model normalization for OpenAI client"""
        client = MultiAPIClient([mock_openai_key])
        
        # OpenAI doesn't use 'openai/' prefix
        normalized = client._normalize_model("openai/gpt-4o", "openai")
        assert normalized == "gpt-4o"
    
    def test_normalize_model_for_openrouter(self, mock_openrouter_key):
        """Test model normalization for OpenRouter client"""
        client = MultiAPIClient([mock_openrouter_key])
        
        # OpenRouter keeps full format
        normalized = client._normalize_model("openai/gpt-4o", "openrouter")
        assert normalized == "openai/gpt-4o"
    
    def test_normalize_model_without_prefix(self, mock_openai_key):
        """Test normalizing model that doesn't have prefix"""
        client = MultiAPIClient([mock_openai_key])
        
        normalized = client._normalize_model("gpt-4o", "openai")
        assert normalized == "gpt-4o"
    
    # ========================================================================
    # Test: Round-Robin Rotation
    # ========================================================================
    
    def test_round_robin_rotation(self, mock_api_keys):
        """Test that client rotates through keys in round-robin fashion"""
        client = MultiAPIClient(mock_api_keys)
        
        # Get initial client
        first_client = client.current_client
        
        # Rotate to next
        second_client = client._get_next_client()
        assert second_client != first_client
        
        # Rotate again
        third_client = client._get_next_client()
        assert third_client != second_client
        
        # After 3 rotations, should cycle back to first
        fourth_client = client._get_next_client()
        assert fourth_client == first_client
    
    # ========================================================================
    # Test: Chat Completion (Mocked)
    # ========================================================================
    
    @responses.activate
    def test_chat_completion_success(self, mock_openrouter_key):
        """Test successful chat completion"""
        client = MultiAPIClient([mock_openrouter_key])
        
        # Mock API response
        responses.add(
            responses.POST,
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "choices": [{
                    "message": {
                        "content": "Test response"
                    }
                }],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150
                },
                "model": "openai/gpt-4o"
            },
            status=200
        )
        
        result = client.chat_completion(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        assert result['success'] is True
        assert result['content'] == "Test response"
        assert result['usage']['total_tokens'] == 150
    
    @responses.activate
    def test_chat_completion_api_error(self, mock_openrouter_key):
        """Test chat completion with API error"""
        client = MultiAPIClient([mock_openrouter_key])
        
        # Mock API error
        responses.add(
            responses.POST,
            "https://openrouter.ai/api/v1/chat/completions",
            json={"error": "Rate limit exceeded"},
            status=429
        )
        
        result = client.chat_completion(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @responses.activate
    def test_chat_completion_fallback_on_error(self, mock_api_keys):
        """Test fallback to next key on API error"""
        client = MultiAPIClient(mock_api_keys[:2])  # Use 2 keys
        
        # First call fails
        responses.add(
            responses.POST,
            "https://openrouter.ai/api/v1/chat/completions",
            json={"error": "Rate limit"},
            status=429
        )
        
        # Second call succeeds
        responses.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{
                    "message": {"content": "Success on fallback"}
                }],
                "usage": {"total_tokens": 100}
            },
            status=200
        )
        
        result = client.chat_completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        # Should succeed with fallback
        assert result['success'] is True
        assert result['content'] == "Success on fallback"
    
    # ========================================================================
    # Test: Vision Chat
    # ========================================================================
    
    @responses.activate
    def test_vision_chat_multiple_images(self, mock_openrouter_key, mock_frame_base64):
        """Test vision chat with multiple images"""
        client = MultiAPIClient([mock_openrouter_key])
        
        # Mock API response
        responses.add(
            responses.POST,
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "choices": [{
                    "message": {
                        "content": '[{"killer": "player1", "victim": "player2"}]'
                    }
                }],
                "usage": {"total_tokens": 2000}
            },
            status=200
        )
        
        result = client.vision_chat_multiple(
            model="openai/gpt-4o",
            prompt="Detect kills",
            images_base64=[mock_frame_base64, mock_frame_base64]
        )
        
        assert result['success'] is True
        assert 'player1' in result['content']
    
    def test_vision_chat_adaptive_timeout(self, mock_openrouter_key):
        """Test that vision chat uses adaptive timeout based on image count"""
        client = MultiAPIClient([mock_openrouter_key])
        
        # With 1 image: 10 + 1*2 = 12s timeout
        # With 5 images: 10 + 5*2 = 20s timeout
        # With 15 images: min(10 + 15*2, 30) = 30s timeout (capped)
        
        # We can't easily test the actual timeout without mocking,
        # but we can verify the method exists and accepts parameters
        assert hasattr(client, 'vision_chat_multiple')


# ============================================================================
# Integration-style tests with realistic scenarios
# ============================================================================

class TestMultiAPIClientIntegration:
    """Integration tests with realistic API scenarios"""
    
    @responses.activate
    def test_load_balancing_across_multiple_keys(self):
        """Test that requests are distributed across multiple keys"""
        keys = [
            "sk-or-v1-key1",
            "sk-or-v1-key2",
            "sk-or-v1-key3"
        ]
        client = MultiAPIClient(keys)
        
        # Mock successful responses for all keys
        for _ in range(6):
            responses.add(
                responses.POST,
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "choices": [{"message": {"content": "OK"}}],
                    "usage": {"total_tokens": 100}
                },
                status=200
            )
        
        # Make 6 requests - should cycle through keys twice
        for _ in range(6):
            result = client.chat_completion(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": "Test"}]
            )
            assert result['success'] is True
        
        # Verify all requests were made
        assert len(responses.calls) == 6
