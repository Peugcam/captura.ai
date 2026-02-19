"""
Configuração do backend Python com validações de segurança
"""
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Setup logging FIRST (before any logging calls)
logger = logging.getLogger(__name__)

# Load environment variables
# Check multiple locations: backend/ (current dir of config.py) OR project root
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent

search_paths = [
    current_dir / '.env',
    project_root / '.env'
]

env_path = None
for path in search_paths:
    if path.exists():
        env_path = path
        break

if env_path:
    load_dotenv(dotenv_path=env_path)
    # logger.info(f"✅ Loaded .env from: {env_path}")  # Commented to avoid early logging
else:
    pass
    # logger.warning(f"⚠️ .env not found in: {[str(p) for p in search_paths]}")

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

# GTA Server Detection (Dual-Server Support)
# Suporta 2 servidores diferentes com layouts de killfeed distintos
GTA_SERVER_TYPE = os.getenv("GTA_SERVER_TYPE", "auto").lower()  # auto, server1, server2
AUTO_DETECT_SERVER = os.getenv("AUTO_DETECT_SERVER", "true").lower() == "true"
SERVER_DETECTION_CONFIDENCE = float(os.getenv("SERVER_DETECTION_CONFIDENCE", "0.80"))  # 80% confiança mínima
# Keywords OTIMIZADAS para GTA kill detection (Inglês + Português)
# Suporta GTA em ambos idiomas
OCR_KEYWORDS = [
    # Tier 1 - Inglês: Mais comuns (80% das kills)
    "KILLED", "WASTED", "SHOT", "DESTROYED",
    # Tier 1 - Português: Mais comuns
    "MATOU", "MORTO", "MORREU", "ATIROU", "DESTRUIU",
    # Tier 2 - Inglês: Comuns (15% das kills)
    "SNIPED", "RIDDLED", "BURNED", "OBLITERATED",
    # Tier 2 - Português: Comuns
    "ABATIDO", "ELIMINADO", "QUEIMADO",
    # Tier 3 - Universal
    "ENDED", "BLASTED"
]
# REMOVIDAS (raras): DEVASTATED, PULVERIZED, FRIED, PLUGGED, POPPED,
# DRILLED, RUINED, RIFLED, FLOORED, SHOTGUNNED, SCOPED, ERASED, VAPORIZED

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
    logger.error(f"❌ No valid API keys found. .env path: {env_path}")
    logger.error(f"   Searched in: {[str(p) for p in search_paths]}")
    raise ValueError(
        "No valid API keys configured!\n"
        "Please set API_KEYS in backend/.env file.\n"
        "Example: API_KEYS=sk-proj-xxxxx,sk-or-v1-xxxxx\n"
        "See backend/.env.example for details."
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

# Advanced Prompt
USE_ADVANCED_PROMPT = os.getenv("USE_ADVANCED_PROMPT", "false").lower() == "true"
EXCEL_FORMAT = "luis_compatible"  # formato compatível com Luis

# LiteLLM Configuration
USE_LITELLM = os.getenv("USE_LITELLM", "false").lower() == "true"
LITELLM_ENABLE_FALLBACK = os.getenv("LITELLM_ENABLE_FALLBACK", "true").lower() == "true"

# API Keys for multiple providers (fallback chain)
LITELLM_API_KEYS = {
    "together": os.getenv("TOGETHER_API_KEY", ""),
    "siliconflow": os.getenv("SILICONFLOW_API_KEY", ""),
    "openrouter": os.getenv("OPENROUTER_API_KEY", ""),
    "openai": os.getenv("OPENAI_API_KEY", ""),
}

# Remove empty keys
LITELLM_API_KEYS = {k: v for k, v in LITELLM_API_KEYS.items() if v and v.strip()}

if USE_LITELLM and not LITELLM_API_KEYS:
    logger.warning("⚠️ LiteLLM enabled but no API keys found. Using legacy client.")
    USE_LITELLM = False

# IPC Configuration (Unix Socket / Named Pipe)
GATEWAY_IPC_MODE = os.getenv("GATEWAY_IPC_MODE", "auto").lower()  # "auto", "unix", "pipe", "http"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Kill Grouping System (economia de API)
# Perfil Híbrido: rápido para kills isoladas, agrupa team fights
QUICK_TIMEOUT = float(os.getenv("QUICK_TIMEOUT", "2.0"))  # Timeout para frame isolado (segundos)
GROUPING_WINDOW = float(os.getenv("GROUPING_WINDOW", "5.0"))  # Janela de agrupamento (segundos)
MAX_FRAMES_BATCH = int(os.getenv("MAX_FRAMES_BATCH", "6"))  # Máximo de frames acumulados
MAX_TOTAL_WAIT = float(os.getenv("MAX_TOTAL_WAIT", "8.0"))  # Timeout total máximo (segundos)
MIN_FRAMES_TO_PROCESS = int(os.getenv("MIN_FRAMES_TO_PROCESS", "1"))  # Mínimo de frames para processar

# Three-Tier Processing System (88% cost reduction)
USE_THREE_TIER = os.getenv("USE_THREE_TIER", "true").lower() == "true"
FRAME_SKIP_INTERVAL = int(os.getenv("FRAME_SKIP_INTERVAL", "2"))  # Process 1 every N frames
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.75"))  # Quality threshold
SAFE_ZONE_INTERVAL = int(os.getenv("SAFE_ZONE_INTERVAL", "15"))  # Full analysis every N frames

# NASA-Level Optimizations
# Frame Deduplication (70% token reduction)
USE_FRAME_DEDUP = os.getenv("USE_FRAME_DEDUP", "true").lower() == "true"
FRAME_SIMILARITY_THRESHOLD = float(os.getenv("FRAME_SIMILARITY_THRESHOLD", "0.95"))

# Gemini Flash 2.0 Support via OpenRouter (90% cheaper than GPT-4o)
# Usa a mesma chave do OpenRouter! Sem necessidade de key separada
USE_GEMINI_FALLBACK = os.getenv("USE_GEMINI_FALLBACK", "true").lower() == "true"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "google/gemini-2.0-flash-exp:free")
