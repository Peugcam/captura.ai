"""
Unit Tests: Gemini Flash 2.0 Client
====================================

Tests the Google Gemini client for vision API operations.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.gemini_client import GeminiClient


@pytest.fixture
def gemini_client():
    """Create a Gemini client instance"""
    return GeminiClient(api_key="test-gemini-api-key")


@pytest.fixture
def sample_image_base64():
    """Sample base64-encoded image"""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def multiple_images_base64():
    """Multiple sample base64-encoded images"""
    return [
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    ]


@pytest.fixture
def mock_success_response():
    """Mock successful Gemini API response"""
    return {
        "candidates": [{
            "content": {
                "parts": [{"text": "Kill detected: player1 killed player2"}]
            }
        }]
    }


# ============================================================================
# Test: Initialization
# ============================================================================

class TestGeminiClientInit:
    """Test client initialization"""

    def test_init_with_api_key(self):
        """Test initialization with valid API key"""
        client = GeminiClient(api_key="test-api-key")

        assert client.api_key == "test-api-key"
        assert client.model == "gemini-2.0-flash-exp"
        assert "googleapis.com" in client.api_base

    def test_init_custom_model(self):
        """Test initialization with custom model"""
        client = GeminiClient(api_key="test-key", model="gemini-pro-vision")

        assert client.model == "gemini-pro-vision"

    def test_init_empty_api_key_raises_error(self):
        """Test that empty API key raises ValueError"""
        with pytest.raises(ValueError, match="API key is required"):
            GeminiClient(api_key="")

    def test_init_none_api_key_raises_error(self):
        """Test that None API key raises ValueError"""
        with pytest.raises(ValueError, match="API key is required"):
            GeminiClient(api_key=None)

    def test_init_whitespace_api_key_raises_error(self):
        """Test that whitespace-only API key raises ValueError"""
        with pytest.raises(ValueError, match="API key is required"):
            GeminiClient(api_key="   ")

    def test_init_strips_whitespace_from_key(self):
        """Test that API key is stripped of whitespace"""
        client = GeminiClient(api_key="  test-key  ")

        assert client.api_key == "test-key"


# ============================================================================
# Test: Vision Chat (Single Image)
# ============================================================================

class TestVisionChat:
    """Test single image vision chat"""

    def test_vision_chat_success(self, gemini_client, sample_image_base64, mock_success_response):
        """Test successful vision chat"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            result = gemini_client.vision_chat(
                prompt="Analyze this image",
                image_base64=sample_image_base64
            )

            assert result["success"] is True
            assert "content" in result
            assert "Kill detected" in result["content"]

    def test_vision_chat_builds_correct_payload(self, gemini_client, sample_image_base64, mock_success_response):
        """Test that payload is built correctly"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            gemini_client.vision_chat(
                prompt="Test prompt",
                image_base64=sample_image_base64,
                temperature=0.7,
                max_tokens=1000
            )

            # Verify payload structure
            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]

            assert "contents" in payload
            assert len(payload["contents"]) == 1
            assert len(payload["contents"][0]["parts"]) == 2
            assert payload["contents"][0]["parts"][0]["text"] == "Test prompt"
            assert payload["contents"][0]["parts"][1]["inline_data"]["data"] == sample_image_base64
            assert payload["generationConfig"]["temperature"] == 0.7
            assert payload["generationConfig"]["maxOutputTokens"] == 1000

    def test_vision_chat_api_error(self, gemini_client, sample_image_base64):
        """Test handling of API error"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.text = "Bad request"

            result = gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            assert result["success"] is False
            assert "error" in result
            assert "400" in result["error"]

    def test_vision_chat_unexpected_response_format(self, gemini_client, sample_image_base64):
        """Test handling of unexpected response format"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"unexpected": "format"}

            result = gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            assert result["success"] is False
            assert "Unexpected response format" in result["error"]

    def test_vision_chat_network_error(self, gemini_client, sample_image_base64):
        """Test handling of network error"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network timeout")

            result = gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            assert result["success"] is False
            assert "error" in result

    def test_vision_chat_timeout(self, gemini_client, sample_image_base64):
        """Test that timeout is set to 30 seconds"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

            gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            call_args = mock_post.call_args
            assert call_args.kwargs["timeout"] == 30


# ============================================================================
# Test: Vision Chat Multiple Images
# ============================================================================

class TestVisionChatMultiple:
    """Test multiple images vision chat"""

    def test_vision_chat_multiple_success(self, gemini_client, multiple_images_base64, mock_success_response):
        """Test successful multi-image vision chat"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            result = gemini_client.vision_chat_multiple(
                prompt="Analyze these images",
                images_base64=multiple_images_base64
            )

            assert result["success"] is True
            assert "content" in result

    def test_vision_chat_multiple_builds_correct_payload(self, gemini_client, multiple_images_base64, mock_success_response):
        """Test that payload includes all images"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            gemini_client.vision_chat_multiple(
                prompt="Test",
                images_base64=multiple_images_base64
            )

            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]

            # Should have 1 text part + 2 image parts
            parts = payload["contents"][0]["parts"]
            assert len(parts) == 3
            assert parts[0]["text"] == "Test"
            assert "inline_data" in parts[1]
            assert "inline_data" in parts[2]

    def test_vision_chat_multiple_extended_timeout(self, gemini_client, multiple_images_base64, mock_success_response):
        """Test that timeout is extended to 60 seconds for multiple images"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            gemini_client.vision_chat_multiple(
                prompt="Test",
                images_base64=multiple_images_base64
            )

            call_args = mock_post.call_args
            assert call_args.kwargs["timeout"] == 60

    def test_vision_chat_multiple_api_error(self, gemini_client, multiple_images_base64):
        """Test handling of API error with multiple images"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal server error"

            result = gemini_client.vision_chat_multiple(
                prompt="Test",
                images_base64=multiple_images_base64
            )

            assert result["success"] is False
            assert "500" in result["error"]

    def test_vision_chat_multiple_empty_images_list(self, gemini_client, mock_success_response):
        """Test with empty images list"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            result = gemini_client.vision_chat_multiple(
                prompt="Test",
                images_base64=[]
            )

            # Should still work (text-only request)
            assert result["success"] is True


# ============================================================================
# Test: Request Construction
# ============================================================================

class TestRequestConstruction:
    """Test HTTP request construction"""

    def test_api_url_construction(self, gemini_client, sample_image_base64, mock_success_response):
        """Test that API URL is constructed correctly"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            call_args = mock_post.call_args
            url = call_args.args[0]

            assert "generativelanguage.googleapis.com" in url
            assert "gemini-2.0-flash-exp" in url
            assert f"key={gemini_client.api_key}" in url

    def test_content_type_header(self, gemini_client, sample_image_base64, mock_success_response):
        """Test that Content-Type header is set"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_success_response

            gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            call_args = mock_post.call_args
            headers = call_args.kwargs["headers"]

            assert headers["Content-Type"] == "application/json"


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error scenarios"""

    def test_missing_candidates_in_response(self, gemini_client, sample_image_base64):
        """Test response with missing candidates"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {}

            result = gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            assert result["success"] is False

    def test_empty_candidates_array(self, gemini_client, sample_image_base64):
        """Test response with empty candidates array"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"candidates": []}

            result = gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            assert result["success"] is False

    def test_missing_content_in_candidate(self, gemini_client, sample_image_base64):
        """Test response with candidate missing content"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"candidates": [{}]}

            result = gemini_client.vision_chat(
                prompt="Test",
                image_base64=sample_image_base64
            )

            assert result["success"] is False


# ============================================================================
# Test: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    def test_kill_feed_detection_workflow(self, gemini_client, sample_image_base64):
        """Test realistic kill feed detection scenario"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": '{"kills": [{"killer": "Alice", "victim": "Bob", "distance": "50m"}]}'
                        }]
                    }
                }]
            }

            result = gemini_client.vision_chat(
                prompt="Detect kills in this image",
                image_base64=sample_image_base64,
                temperature=0.0,
                max_tokens=2000
            )

            assert result["success"] is True
            assert "Alice" in result["content"]
            assert "Bob" in result["content"]

    def test_multiple_frames_processing(self, gemini_client, multiple_images_base64):
        """Test processing multiple frames"""
        with patch('src.gemini_client.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": "Frame 1: 1 kill | Frame 2: 2 kills"
                        }]
                    }
                }]
            }

            result = gemini_client.vision_chat_multiple(
                prompt="Analyze kills in these frames",
                images_base64=multiple_images_base64
            )

            assert result["success"] is True
            assert "Frame 1" in result["content"]
            assert "Frame 2" in result["content"]
