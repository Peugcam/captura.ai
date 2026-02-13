"""
Security utilities and validators for GTA Analytics V2
Provides common security functions to prevent vulnerabilities
"""

import re
import os
import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Centralized security validation utilities"""

    @staticmethod
    def validate_filename(filename: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """
        Valida nome de arquivo para prevenir path traversal e injeção

        Args:
            filename: Nome do arquivo a validar
            allowed_extensions: Lista de extensões permitidas (ex: ['.xlsx', '.pdf'])

        Returns:
            True se o nome é seguro

        Raises:
            ValueError: Se o nome do arquivo é inválido
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Remover espaços extras
        filename = filename.strip()

        # Verificar caracteres perigosos
        dangerous_chars = ['..', '/', '\\', '\x00', '\n', '\r']
        for char in dangerous_chars:
            if char in filename:
                raise ValueError(f"Invalid character in filename: {char}")

        # Verificar tamanho
        if len(filename) > 255:
            raise ValueError("Filename too long (max 255 characters)")

        # Verificar extensão se especificada
        if allowed_extensions:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in [e.lower() for e in allowed_extensions]:
                raise ValueError(f"Invalid file extension. Allowed: {allowed_extensions}")

        # Verificar nomes reservados do Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        name_without_ext = os.path.splitext(filename)[0].upper()
        if name_without_ext in reserved_names:
            raise ValueError(f"Reserved filename: {name_without_ext}")

        return True

    @staticmethod
    def validate_path(filepath: str, base_dir: str) -> str:
        """
        Valida que um caminho está dentro do diretório base permitido

        Args:
            filepath: Caminho do arquivo
            base_dir: Diretório base permitido

        Returns:
            Caminho absoluto validado

        Raises:
            ValueError: Se o path está fora do diretório permitido
        """
        # Resolver para caminhos absolutos
        base_abs = os.path.abspath(base_dir)
        file_abs = os.path.abspath(filepath)

        # Verificar que está dentro do diretório base
        if not file_abs.startswith(base_abs):
            raise ValueError(f"Path traversal detected: {filepath}")

        return file_abs

    @staticmethod
    def sanitize_log_message(message: str, max_length: int = 1000) -> str:
        """
        Sanitiza mensagem de log para prevenir log injection

        Args:
            message: Mensagem original
            max_length: Comprimento máximo

        Returns:
            Mensagem sanitizada
        """
        if not message:
            return ""

        # Remover caracteres de controle (exceto tab e espaço)
        sanitized = ''.join(char if char.isprintable() or char in '\t\n' else '' for char in message)

        # Limitar tamanho
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "...[truncated]"

        # Substituir múltiplas quebras de linha
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)

        return sanitized

    @staticmethod
    def mask_sensitive_data(data: str, reveal_chars: int = 4) -> str:
        """
        Mascara dados sensíveis (API keys, tokens, etc)

        Args:
            data: Dado sensível
            reveal_chars: Quantos caracteres mostrar no início e fim

        Returns:
            Dado mascarado
        """
        if not data or len(data) <= reveal_chars * 2:
            return "***"

        return f"{data[:reveal_chars]}...{data[-reveal_chars:]}"

    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """
        Valida formato básico de API key

        Args:
            api_key: Chave API a validar

        Returns:
            True se o formato parece válido
        """
        if not api_key or len(api_key) < 20:
            return False

        # Lista de placeholders conhecidos
        invalid_patterns = [
            'your_api_key', 'api_key_here', 'sk-xxx', 'sk-...',
            'example', 'test', 'placeholder', 'demo'
        ]

        api_key_lower = api_key.lower()
        for pattern in invalid_patterns:
            if pattern in api_key_lower:
                return False

        return True

    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """
        Valida URL para prevenir SSRF

        Args:
            url: URL a validar
            allowed_schemes: Esquemas permitidos (ex: ['http', 'https'])

        Returns:
            True se a URL é segura

        Raises:
            ValueError: Se a URL é inválida
        """
        if not url:
            raise ValueError("URL cannot be empty")

        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']

        # Parse básico
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {e}")

        # Verificar esquema
        if parsed.scheme not in allowed_schemes:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Allowed: {allowed_schemes}")

        # Verificar se não é localhost/IP privado em produção
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        if parsed.hostname in blocked_hosts:
            logger.warning(f"⚠️  URL points to localhost: {url}")

        return True

    @staticmethod
    def sanitize_dict_for_logging(data: dict, sensitive_keys: Optional[List[str]] = None) -> dict:
        """
        Sanitiza dicionário para logging, mascarando chaves sensíveis

        Args:
            data: Dicionário a sanitizar
            sensitive_keys: Lista de chaves sensíveis (ex: ['api_key', 'password'])

        Returns:
            Dicionário sanitizado
        """
        if sensitive_keys is None:
            sensitive_keys = ['api_key', 'api_keys', 'password', 'token', 'secret', 'auth']

        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = SecurityValidator.sanitize_dict_for_logging(value, sensitive_keys)
            else:
                sanitized[key] = value

        return sanitized


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: Máximo de requisições permitidas
            window_seconds: Janela de tempo em segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {client_id: [timestamps]}

    def is_allowed(self, client_id: str) -> bool:
        """
        Verifica se o cliente pode fazer uma requisição

        Args:
            client_id: Identificador único do cliente

        Returns:
            True se permitido, False se excedeu o limite
        """
        import time

        current_time = time.time()

        # Inicializar ou limpar requisições antigas
        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remover timestamps fora da janela
        self.requests[client_id] = [
            ts for ts in self.requests[client_id]
            if current_time - ts < self.window_seconds
        ]

        # Verificar limite
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Adicionar nova requisição
        self.requests[client_id].append(current_time)
        return True

    def get_remaining(self, client_id: str) -> int:
        """
        Retorna quantas requisições ainda são permitidas

        Args:
            client_id: Identificador único do cliente

        Returns:
            Número de requisições restantes
        """
        if client_id not in self.requests:
            return self.max_requests

        return max(0, self.max_requests - len(self.requests[client_id]))


# Singleton global para rate limiting
global_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


# ============================================================================
# API Authentication
# ============================================================================

import secrets
import hashlib
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional

# API Key Header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Load API token from environment (for internal services like gateway)
# In production, this should be a strong random token
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

if not INTERNAL_API_TOKEN:
    # Generate a secure token if not provided (development only)
    INTERNAL_API_TOKEN = secrets.token_urlsafe(32)
    logger.warning(f"⚠️  No INTERNAL_API_TOKEN set. Generated temporary token: {INTERNAL_API_TOKEN[:16]}...")
    logger.warning("   Set INTERNAL_API_TOKEN in .env for production!")

# Hash the token for comparison (prevents timing attacks)
TOKEN_HASH = hashlib.sha256(INTERNAL_API_TOKEN.encode()).hexdigest()


def verify_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """
    Verify API key from request header

    Args:
        api_key: API key from X-API-Key header

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if api_key is None:
        logger.warning("🔒 API request rejected: Missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Constant-time comparison to prevent timing attacks
    provided_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if not secrets.compare_digest(provided_hash, TOKEN_HASH):
        logger.warning(f"🔒 API request rejected: Invalid API key {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return api_key


# Public endpoints (no authentication required)
PUBLIC_ENDPOINTS = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json"
]


def is_public_endpoint(path: str) -> bool:
    """Check if endpoint is public (no auth required)"""
    return any(path.startswith(endpoint) for endpoint in PUBLIC_ENDPOINTS)
