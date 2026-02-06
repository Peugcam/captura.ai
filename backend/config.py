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
OCR_KEYWORDS = ["MATOU", "KILL", "ELIMINADO", "WASTED"]

# Vision AI
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
VISION_MODEL = os.getenv("VISION_MODEL", "openai/gpt-4o")
BATCH_SIZE_QUICK = int(os.getenv("BATCH_SIZE_QUICK", "5"))
BATCH_SIZE_DEEP = int(os.getenv("BATCH_SIZE_DEEP", "15"))
QUICK_BATCH_INTERVAL = float(os.getenv("QUICK_BATCH_INTERVAL", "2.0"))  # segundos
DEEP_BATCH_INTERVAL = float(os.getenv("DEEP_BATCH_INTERVAL", "60.0"))  # segundos

# Backend Server
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "3000"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")

# Export
EXPORT_DIR = os.getenv("EXPORT_DIR", "./exports")
EXCEL_FORMAT = "luis_compatible"  # formato compatível com Luis

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
