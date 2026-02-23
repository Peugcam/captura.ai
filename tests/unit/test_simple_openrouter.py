"""
Unit Tests: Simple OpenRouter Client
=====================================

Tests the direct OpenRouter API client (legacy, without LiteLLM).
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import requests

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.simple_openrouter import SimpleOpenRouter


@pytest.fixture
def openrouter_client():
    """Create an OpenRouter client instance"""
    return SimpleOpenRouter(api_key="test-openrouter-key")


@pytest.fixture
def sample_messages():
    """Sample chat messages"""
    return [
        {"role": "user", "content": "Analyze this GTA kill feed"}
    ]


@pytest.fixture
def sample_image_base64():
    """Sample base64-encoded image"""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def multiple_images_base64():
    """Multiple sample images"""
    return [
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    ]


@pytest.fixture
def mock_openrouter_response():
    """Mock successful OpenRouter API response"""
    return {
        "choices": [{
            "message": {
                "content": "Kill: player1 killed player2"
            }
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        },
        "model": "openai/gpt-4o"
    }


# ============================================================================
# Test: Initialization
# ============================================================================

class TestSimpleOpenRouterInit:
    """Test client initialization"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        client = SimpleOpenRouter(api_key="test-key")

        assert client.api_key == "test-key"
        assert "openrouter.ai" in client.api_base

    def test_api_base_url(self):
        """Test that API base URL is correct"""
        client = SimpleOpenRouter(api_key="test-key")

        assert client.api_base == "https://openrouter.ai/api/v1"


# ============================================================================
# Test: Chat Completion
# ============================================================================

class TestChatCompletion:
    """Test chat completion functionality"""

    def test_chat_completion_success(self, openrouter_client, sample_messages, mock_openrouter_response):
        """Test successful chat completion"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            assert result["success"] is True
            assert "content" in result
            assert "usage" in result
            assert result["usage"]["prompt_tokens"] == 50
            assert result["usage"]["completion_tokens"] == 20

    def test_chat_completion_builds_correct_request(self, openrouter_client, sample_messages, mock_openrouter_response):
        """Test that request is built correctly"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages,
                temperature=0.5,
                max_tokens=1000
            )

            call_args = mock_post.call_args
            assert call_args.args[0] == "https://openrouter.ai/api/v1/chat/completions"

            payload = call_args.kwargs["json"]
            assert payload["model"] == "openai/gpt-4o"
            assert payload["messages"] == sample_messages
            assert payload["temperature"] == 0.5
            assert payload["max_tokens"] == 1000

    def test_chat_completion_headers(self, openrouter_client, sample_messages, mock_openrouter_response):
        """Test that headers are set correctly"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]

            assert "Bearer" in headers["Authorization"]
            assert headers["Content-Type"] == "application/json"
            assert "X-Title" in headers

    def test_chat_completion_timeout(self, openrouter_client, sample_messages, mock_openrouter_response):
        """Test that custom timeout is used"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages,
                timeout=60
            )

            call_args = mock_post.call_args
            assert call_args.kwargs["timeout"] == 60

    def test_chat_completion_api_error(self, openrouter_client, sample_messages):
        """Test handling of API error"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.HTTPError("API Error")

            result = openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            assert result["success"] is False
            assert "error" in result

    def test_chat_completion_network_error(self, openrouter_client, sample_messages):
        """Test handling of network error"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

            result = openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            assert result["success"] is False
            assert "error" in result

    def test_chat_completion_missing_usage_data(self, openrouter_client, sample_messages):
        """Test handling of response without usage data"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": "Response"}}]
            }
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            assert result["success"] is True
            assert result["usage"]["prompt_tokens"] == 0
            assert result["usage"]["completion_tokens"] == 0


# ============================================================================
# Test: Vision Chat (Single Image)
# ============================================================================

class TestVisionChat:
    """Test single image vision chat"""

    def test_vision_chat_success(self, openrouter_client, sample_image_base64, mock_openrouter_response):
        """Test successful vision chat"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.vision_chat(
                model="openai/gpt-4o",
                prompt="Analyze this image",
                image_base64=sample_image_base64
            )

            assert result["success"] is True
            assert "content" in result

    def test_vision_chat_builds_correct_messages(self, openrouter_client, sample_image_base64, mock_openrouter_response):
        """Test that messages are built correctly for vision"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            openrouter_client.vision_chat(
                model="openai/gpt-4o",
                prompt="Test prompt",
                image_base64=sample_image_base64
            )

            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]
            messages = payload["messages"]

            assert len(messages) == 1
            assert messages[0]["role"] == "user"

            content = messages[0]["content"]
            assert len(content) == 2
            assert content[0]["type"] == "text"
            assert content[0]["text"] == "Test prompt"
            assert content[1]["type"] == "image_url"
            assert "base64" in content[1]["image_url"]["url"]


# ============================================================================
# Test: Vision Chat Multiple Images
# ============================================================================

class TestVisionChatMultiple:
    """Test multiple images vision chat"""

    def test_vision_chat_multiple_success(self, openrouter_client, multiple_images_base64, mock_openrouter_response):
        """Test successful multi-image vision chat"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.vision_chat_multiple(
                model="openai/gpt-4o",
                prompt="Analyze these frames",
                images_base64=multiple_images_base64
            )

            assert result["success"] is True

    def test_vision_chat_multiple_builds_correct_messages(self, openrouter_client, multiple_images_base64, mock_openrouter_response):
        """Test that messages include all images"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            openrouter_client.vision_chat_multiple(
                model="openai/gpt-4o",
                prompt="Test",
                images_base64=multiple_images_base64
            )

            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]
            messages = payload["messages"]

            content = messages[0]["content"]
            # Should have 1 text + 2 images
            assert len(content) == 3
            assert content[0]["type"] == "text"
            assert content[1]["type"] == "image_url"
            assert content[2]["type"] == "image_url"

    def test_vision_chat_multiple_adaptive_timeout(self, openrouter_client, multiple_images_base64, mock_openrouter_response):
        """Test adaptive timeout based on image count"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            # 2 images: 10 + (2 * 2) = 14 seconds
            openrouter_client.vision_chat_multiple(
                model="openai/gpt-4o",
                prompt="Test",
                images_base64=multiple_images_base64
            )

            call_args = mock_post.call_args
            timeout = call_args.kwargs["timeout"]
            assert timeout == 14

    def test_vision_chat_multiple_max_timeout(self, openrouter_client, mock_openrouter_response):
        """Test that timeout caps at 30 seconds"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            # 20 images: 10 + (20 * 2) = 50, capped at 30
            many_images = ["img"] * 20

            openrouter_client.vision_chat_multiple(
                model="openai/gpt-4o",
                prompt="Test",
                images_base64=many_images
            )

            call_args = mock_post.call_args
            timeout = call_args.kwargs["timeout"]
            assert timeout == 30  # Capped at max

    def test_vision_chat_multiple_empty_images(self, openrouter_client, mock_openrouter_response):
        """Test with empty images list"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_openrouter_response
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.vision_chat_multiple(
                model="openai/gpt-4o",
                prompt="Test",
                images_base64=[]
            )

            # Should still work (text-only)
            assert result["success"] is True


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases"""

    def test_timeout_error(self, openrouter_client, sample_messages):
        """Test handling of timeout"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

            result = openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            assert result["success"] is False
            assert "timed out" in result["error"].lower()

    def test_malformed_response(self, openrouter_client, sample_messages):
        """Test handling of malformed JSON response"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            # Need to raise during raise_for_status or make json() fail as RequestException
            mock_post.side_effect = requests.exceptions.RequestException("Invalid response")

            result = openrouter_client.chat_completion(
                model="openai/gpt-4o",
                messages=sample_messages
            )

            assert result["success"] is False


# ============================================================================
# Test: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic usage scenarios"""

    def test_kill_feed_analysis_workflow(self, openrouter_client, sample_image_base64):
        """Test realistic kill feed analysis"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '{"kills": [{"killer": "Alice", "victim": "Bob"}]}'
                    }
                }],
                "usage": {"prompt_tokens": 100, "completion_tokens": 30, "total_tokens": 130},
                "model": "openai/gpt-4o"
            }
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.vision_chat(
                model="openai/gpt-4o",
                prompt="Detect kills in this frame",
                image_base64=sample_image_base64
            )

            assert result["success"] is True
            assert "Alice" in result["content"]
            assert "Bob" in result["content"]

    def test_batch_frame_processing(self, openrouter_client, multiple_images_base64):
        """Test processing multiple frames in batch"""
        with patch('src.simple_openrouter.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Frame 1: 2 kills | Frame 2: 1 kill"
                    }
                }],
                "usage": {"prompt_tokens": 200, "completion_tokens": 40, "total_tokens": 240},
                "model": "openai/gpt-4o"
            }
            mock_post.return_value.raise_for_status = Mock()

            result = openrouter_client.vision_chat_multiple(
                model="openai/gpt-4o",
                prompt="Analyze all kills in these frames",
                images_base64=multiple_images_base64
            )

            assert result["success"] is True
            assert "Frame 1" in result["content"]
            assert "Frame 2" in result["content"]
