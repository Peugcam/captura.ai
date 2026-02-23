"""
Pytest Configuration and Shared Fixtures
=========================================

Provides common fixtures for all tests.
"""

import pytest
import base64
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List
from PIL import Image
import io


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_api_keys() -> List[str]:
    """Mock API keys for testing"""
    return [
        "sk-or-v1-test-key-1-abcdef123456",
        "sk-proj-test-key-2-ghijkl789012",
        "sk-or-v1-test-key-3-mnopqr345678"
    ]


@pytest.fixture
def mock_openrouter_key() -> str:
    """Single OpenRouter API key"""
    return "sk-or-v1-test-openrouter-key-abc123"


@pytest.fixture
def mock_openai_key() -> str:
    """Single OpenAI API key"""
    return "sk-proj-test-openai-key-xyz789"


# ============================================================================
# Frame and Image Fixtures
# ============================================================================

@pytest.fixture
def mock_frame_base64() -> str:
    """Generate a mock frame in base64 format"""
    # Create a simple test image
    img = Image.new('RGB', (1920, 1080), color='black')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64


@pytest.fixture
def mock_frame_with_text() -> str:
    """Generate a mock frame with kill feed text"""
    from PIL import ImageDraw, ImageFont
    
    # Create image
    img = Image.new('RGB', (1920, 1080), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Add kill feed text (top-right corner)
    kill_text = "PPP almeida99 MATOU 💀 LLL pikachu1337 120m"
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((1200, 100), kill_text, fill=(255, 255, 255), font=font)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64


@pytest.fixture
def mock_frame_data() -> Dict:
    """Mock frame data structure from Gateway"""
    return {
        "data": "base64_encoded_image_data_here",
        "timestamp": 1707565200000,
        "number": 1,
        "received_at": 1707565200
    }


# ============================================================================
# Kill Data Fixtures
# ============================================================================

@pytest.fixture
def mock_kill_data() -> Dict:
    """Mock kill data from parser"""
    return {
        'killer': 'almeida99',
        'killer_team': 'PPP',
        'victim': 'pikachu1337',
        'victim_team': 'LLL',
        'distance': '120m',
        'keyword': 'MATOU',
        'timestamp': '2026-02-10T08:00:00',
        'confirmed': True
    }


@pytest.fixture
def mock_kill_feed_lines() -> List[str]:
    """Mock OCR results from kill feed"""
    return [
        "PPP almeida99 MATOU 💀 LLL pikachu1337 120m",
        "AAA jogador123 ELIMINOU 🔫 BBB player456 85m",
        "CCC sniper99 KILLED 💥 DDD target777",
        "Invalid line without kill keyword",
        "EEE killer MATOU FFF victim"
    ]


@pytest.fixture
def mock_multiple_kills() -> List[Dict]:
    """Mock multiple kills for team tracker testing"""
    return [
        {
            'killer': 'alice',
            'killer_team': 'TeamA',
            'victim': 'bob',
            'victim_team': 'TeamB',
            'distance': '100m'
        },
        {
            'killer': 'charlie',
            'killer_team': 'TeamA',
            'victim': 'david',
            'victim_team': 'TeamC',
            'distance': '50m'
        },
        {
            'killer': 'alice',
            'killer_team': 'TeamA',
            'victim': 'eve',
            'victim_team': 'TeamB',
            'distance': '150m'
        }
    ]


# ============================================================================
# API Response Fixtures
# ============================================================================

@pytest.fixture
def mock_vision_api_response() -> Dict:
    """Mock successful Vision API response"""
    return {
        "success": True,
        "content": json.dumps([
            {
                "killer": "almeida99",
                "killer_team": "PPP",
                "victim": "pikachu1337",
                "victim_team": "LLL",
                "distance": "120m"
            }
        ]),
        "usage": {
            "prompt_tokens": 1500,
            "completion_tokens": 150,
            "total_tokens": 1650
        },
        "model": "gpt-4o",
        "api_type": "openrouter"
    }


@pytest.fixture
def mock_vision_api_error() -> Dict:
    """Mock failed Vision API response"""
    return {
        "success": False,
        "content": "",
        "usage": {},
        "model": "gpt-4o",
        "error": "API rate limit exceeded",
        "api_type": "openrouter"
    }


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def temp_export_dir():
    """Create temporary directory for export tests"""
    temp_dir = tempfile.mkdtemp(prefix="gta_test_exports_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_test_frames_dir():
    """Create temporary directory with test frames"""
    temp_dir = tempfile.mkdtemp(prefix="gta_test_frames_")
    
    # Create some test frame files
    for i in range(3):
        img = Image.new('RGB', (1920, 1080), color=(i*50, i*50, i*50))
        img.save(Path(temp_dir) / f"frame_{i:04d}.jpg", quality=85)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Match Data Fixtures
# ============================================================================

@pytest.fixture
def mock_match_summary() -> Dict:
    """Mock match summary for export testing"""
    return {
        'total_kills': 15,
        'total_players': 100,
        'alive_players': 25,
        'dead_players': 75,
        'active_teams': 8,
        'teams': [
            {
                'name': 'TeamA',
                'alive': 5,
                'dead': 5,
                'total': 10,
                'kills': 8,
                'deaths': 5
            },
            {
                'name': 'TeamB',
                'alive': 3,
                'dead': 7,
                'total': 10,
                'kills': 5,
                'deaths': 8
            }
        ],
        'leaderboard': [
            {'name': 'player1', 'team': 'TeamA', 'kills': 5, 'deaths': 1},
            {'name': 'player2', 'team': 'TeamB', 'kills': 3, 'deaths': 2}
        ]
    }


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("API_KEYS", "sk-or-v1-test-key-1,sk-proj-test-key-2")
    monkeypatch.setenv("VISION_MODEL", "openai/gpt-4o")
    monkeypatch.setenv("OCR_ENABLED", "true")
    monkeypatch.setenv("GAME_TYPE", "gta")
    monkeypatch.setenv("GATEWAY_URL", "http://localhost:8000")
    monkeypatch.setenv("TEST_MODE", "true")
