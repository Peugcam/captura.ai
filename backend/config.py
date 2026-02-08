"""
Configuração do backend Python
"""
import os
from dotenv import load_dotenv

load_dotenv()

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

# Vision AI - Multiple API Keys Support
# Parse comma-separated API keys from environment
API_KEYS_STR = os.getenv("API_KEYS", os.getenv("OPENROUTER_API_KEY", ""))
API_KEYS = [key.strip() for key in API_KEYS_STR.split(",") if key.strip()]

# Legacy support
if not API_KEYS:
    raise ValueError("No API keys configured! Set API_KEYS in .env")

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
