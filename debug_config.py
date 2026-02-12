
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path para importar config
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    import config
    print("="*60)
    print("DEBUG CONFIGURATION")
    print("="*60)
    print(f"Current Directory: {os.getcwd()}")
    print(f"Config File: {config.__file__}")
    print(f"GATEWAY_URL: {config.GATEWAY_URL}")
    print(f"BACKEND_PORT: {config.BACKEND_PORT}")
    print(f"OCR_ENABLED: {config.OCR_ENABLED}")
    
    # Check .env file existence
    env_current = Path('.') / '.env'
    env_parent = Path('..') / '.env'
    env_backend = Path('backend') / '.env'
    
    print(f"Check .env in current: {env_current.absolute()} -> {env_current.exists()}")
    print(f"Check .env in parent: {env_parent.absolute()} -> {env_parent.exists()}")
    print(f"Check .env in backend: {env_backend.absolute()} -> {env_backend.exists()}")
    
    print("="*60)
    
except Exception as e:
    print(f"ERROR importing config: {e}")
