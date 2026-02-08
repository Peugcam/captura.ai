"""
Configuração do backend Python com validações de segurança
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

def validate_api_key(key: str) -> bool:
    """
    Valida formato básico de API keys

    Args:
        key: API key para validar

    Returns:
        True se o formato é válido
    """
    key = key.strip()

    # Verificar tamanho mínimo
    if len(key) < 20:
        return False

    # Verificar se não é placeholder
    placeholders = ['your_api_key_here', 'your_openai_key', 'your_openrouter_key',
                   'sk-...', 'sk-xxx', 'example', 'placeholder', 'test']
    if any(placeholder in key.lower() for placeholder in placeholders):
        return False

    # Verificar formato conhecido
    valid_prefixes = ['sk-or-', 'sk-proj-', 'sk-']
    if not any(key.startswith(prefix) for prefix in valid_prefixes):
        logger.warning(f"API key with unknown format detected: {key[:10]}...")
        return True  # Aceita, mas avisa

    return True

def sanitize_config_value(value: str, is_sensitive: bool = False) -> str:
    """
    Sanitiza valores de configuração para logging seguro

    Args:
        value: Valor a sanitizar
        is_sensitive: Se é dado sensível (API key, senha, etc)

    Returns:
        Valor sanitizado
    """
    if is_sensitive and value:
        # Mostra apenas primeiros e últimos 4 caracteres
        if len(value) > 12:
            return f"{value[:4]}...{value[-4:]}"
        return "***"
    return value

# Gateway Go
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))  # segundos
FRAMES_BATCH_SIZE = int(os.getenv("FRAMES_BATCH_SIZE", "10"))

# OCR Pre-Filter
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
OCR_WORKERS = int(os.getenv("OCR_WORKERS", "4"))
# Game Type (para otimizar prompts e ROI)
GAME_TYPE = os.getenv("GAME_TYPE", "gta").lower()  # gta ou naruto
USE_ROI = os.getenv("USE_ROI", "true").lower() == "true"
# Keywords para GTA kill detection (verbos reais do GTA V)
OCR_KEYWORDS = [
    # Genéricos
    "KILLED", "SHOT", "DIED", "WASTED",
    # Pistols
    "PLUGGED", "POPPED", "BLASTED",
    # SMGs
    "RIDDLED", "DRILLED", "RUINED",
    # Rifles
    "RIFLED", "FLOORED", "ENDED",
    # Shotguns
    "DEVASTATED", "PULVERIZED", "SHOTGUNNED",
    # Snipers
    "SNIPED", "SCOPED",
    # Explosivos
    "OBLITERATED", "DESTROYED", "ERASED", "VAPORIZED",
    # Fogo
    "BURNED", "FRIED"
]

# Vision AI - Multiple API Keys Support with validation
# Parse comma-separated API keys from environment
API_KEYS_STR = os.getenv("API_KEYS", os.getenv("OPENROUTER_API_KEY", ""))
API_KEYS_RAW = [key.strip() for key in API_KEYS_STR.split(",") if key.strip()]

# Validate API keys
API_KEYS = []
for key in API_KEYS_RAW:
    if validate_api_key(key):
        API_KEYS.append(key)
        logger.info(f"✅ Valid API key loaded: {sanitize_config_value(key, is_sensitive=True)}")
    else:
        logger.error(f"❌ Invalid API key format detected and skipped: {key[:10]}...")

# Ensure at least one valid key
if not API_KEYS:
    raise ValueError(
        "No valid API keys configured!\n"
        "Please set API_KEYS in .env file.\n"
        "Example: API_KEYS=sk-proj-xxxxx,sk-or-v1-xxxxx\n"
        "See .env.example for details."
    )

VISION_MODEL = os.getenv("VISION_MODEL", "openai/gpt-4o")
BATCH_SIZE_QUICK = int(os.getenv("BATCH_SIZE_QUICK", "10"))  # Processar 10 frames por vez
BATCH_SIZE_DEEP = int(os.getenv("BATCH_SIZE_DEEP", "15"))
QUICK_BATCH_INTERVAL = float(os.getenv("QUICK_BATCH_INTERVAL", "2.0"))  # Processar a cada 2 segundos
DEEP_BATCH_INTERVAL = float(os.getenv("DEEP_BATCH_INTERVAL", "60.0"))  # segundos

# Backend Server
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "3000"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")

# Export
EXPORT_DIR = os.getenv("EXPORT_DIR", "./exports")
EXCEL_FORMAT = "luis_compatible"  # formato compatível com Luis

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
