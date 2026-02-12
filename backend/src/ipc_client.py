"""
IPC Client for Gateway communication via Unix Domain Sockets / Named Pipes
Falls back to HTTP if IPC is not available
"""

import asyncio
import logging
import platform
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class IPCGatewayClient:
    """
    Client for communicating with Gateway via IPC (Unix Socket/Named Pipe)
    Falls back to HTTP if IPC is unavailable
    """

    def __init__(self, gateway_url: str = "http://localhost:8000", ipc_mode: str = "auto"):
        """
        Initialize IPC client

        Args:
            gateway_url: HTTP URL for fallback (e.g., "http://localhost:8000")
            ipc_mode: "unix", "pipe", "http", or "auto" (auto-detect)
        """
        self.gateway_url = gateway_url
        self.ipc_mode = ipc_mode
        self.client: Optional[httpx.AsyncClient] = None
        self.using_ipc = False

        # Platform-specific IPC paths
        if platform.system() == "Windows":
            self.ipc_path = r"\\.\pipe\gta-gateway"
            self.default_ipc_mode = "pipe"
        else:
            self.ipc_path = "/tmp/gta-gateway.sock"
            self.default_ipc_mode = "unix"

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def connect(self):
        """Establish connection to Gateway (IPC or HTTP fallback)"""
        # Determine IPC mode
        if self.ipc_mode == "auto":
            ipc_mode = self.default_ipc_mode
        elif self.ipc_mode in ["unix", "pipe"]:
            ipc_mode = self.ipc_mode
        else:
            ipc_mode = "http"  # Force HTTP mode

        # Try IPC first (if not explicitly set to HTTP)
        if ipc_mode in ["unix", "pipe"] and self._is_ipc_available():
            try:
                if ipc_mode == "unix":
                    # Unix Domain Socket
                    transport = httpx.AsyncHTTPTransport(uds=self.ipc_path)
                    self.client = httpx.AsyncClient(
                        transport=transport,
                        base_url="http://localhost"  # Required but ignored for Unix sockets
                    )
                    self.using_ipc = True
                    logger.info(f"Connected to Gateway via Unix Socket: {self.ipc_path}")

                elif ipc_mode == "pipe":
                    # Named Pipe (Windows)
                    # Note: httpx doesn't directly support Named Pipes, so we fall back to HTTP
                    logger.warning("Named Pipes not yet fully supported in httpx, using HTTP fallback")
                    raise Exception("Named Pipe not supported")

            except Exception as e:
                logger.warning(f"Failed to connect via IPC: {e}, falling back to HTTP")
                self.using_ipc = False

        # Fallback to HTTP
        if not self.using_ipc:
            self.client = httpx.AsyncClient(base_url=self.gateway_url, timeout=10.0)
            logger.info(f"Connected to Gateway via HTTP: {self.gateway_url}")

        # Test connection
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            logger.info(f"Gateway health check passed (IPC={self.using_ipc})")
        except Exception as e:
            logger.error(f"Gateway health check failed: {e}")
            raise

    def _is_ipc_available(self) -> bool:
        """Check if IPC path exists"""
        import os
        import stat

        try:
            if platform.system() == "Windows":
                # On Windows, check if pipe exists is tricky
                # We'll just try to connect later
                return True
            else:
                # On Linux/Mac, check if socket file exists
                return os.path.exists(self.ipc_path) and stat.S_ISSOCK(os.stat(self.ipc_path).st_mode)
        except Exception:
            return False

    async def get_frames(self, max_frames: int = 10) -> List[Dict]:
        """
        Fetch frames from Gateway

        Args:
            max_frames: Maximum number of frames to fetch

        Returns:
            List of frame dictionaries
        """
        try:
            response = await self.client.get("/frames")

            if response.status_code == 204:  # No Content
                return []

            response.raise_for_status()
            data = response.json()
            return data.get("frames", [])

        except httpx.HTTPStatusError as e:
            if e.response.status_code != 204:
                logger.error(f"HTTP error fetching frames: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching frames: {e}")
            return []

    async def get_stats(self) -> Dict:
        """
        Get Gateway statistics

        Returns:
            Stats dictionary
        """
        try:
            response = await self.client.get("/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {}

    async def get_health(self) -> Dict:
        """
        Get Gateway health status

        Returns:
            Health status dictionary
        """
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching health: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Close client connection"""
        if self.client:
            await self.client.aclose()
            logger.info("Gateway client closed")

    def is_using_ipc(self) -> bool:
        """Check if client is using IPC (vs HTTP)"""
        return self.using_ipc


# Convenience function for backward compatibility
async def create_gateway_client(
    gateway_url: str = "http://localhost:8000",
    ipc_mode: str = "auto"
) -> IPCGatewayClient:
    """
    Create and connect to Gateway client

    Args:
        gateway_url: HTTP URL for fallback
        ipc_mode: "unix", "pipe", "http", or "auto"

    Returns:
        Connected IPCGatewayClient
    """
    client = IPCGatewayClient(gateway_url=gateway_url, ipc_mode=ipc_mode)
    await client.connect()
    return client
