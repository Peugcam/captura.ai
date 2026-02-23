"""
Unit Tests: IPC Gateway Client
===============================

Tests the IPC client that communicates with the Gateway via Unix sockets
or Named Pipes with HTTP fallback.
"""

import pytest
import sys
import platform
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import httpx

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.ipc_client import IPCGatewayClient, create_gateway_client


# ============================================================================
# Test: Initialization
# ============================================================================

class TestIPCClientInit:
    """Test IPC client initialization"""

    def test_init_default_parameters(self):
        """Test initialization with default parameters"""
        client = IPCGatewayClient()
        assert client.gateway_url == "http://localhost:8000"
        assert client.ipc_mode == "auto"
        assert client.client is None
        assert client.using_ipc is False

    def test_init_custom_url(self):
        """Test initialization with custom gateway URL"""
        client = IPCGatewayClient(gateway_url="http://localhost:9000")
        assert client.gateway_url == "http://localhost:9000"

    def test_init_custom_ipc_mode(self):
        """Test initialization with custom IPC mode"""
        client = IPCGatewayClient(ipc_mode="http")
        assert client.ipc_mode == "http"

    @patch('platform.system', return_value='Linux')
    def test_init_sets_unix_socket_path_on_linux(self, mock_platform):
        """Test Unix socket path on Linux"""
        client = IPCGatewayClient()
        assert client.ipc_path == "/tmp/gta-gateway.sock"
        assert client.default_ipc_mode == "unix"

    @patch('platform.system', return_value='Windows')
    def test_init_sets_named_pipe_path_on_windows(self, mock_platform):
        """Test Named Pipe path on Windows"""
        client = IPCGatewayClient()
        assert client.ipc_path == r"\\.\pipe\gta-gateway"
        assert client.default_ipc_mode == "pipe"

    @patch('platform.system', return_value='Darwin')
    def test_init_sets_unix_socket_path_on_macos(self, mock_platform):
        """Test Unix socket path on macOS"""
        client = IPCGatewayClient()
        assert client.ipc_path == "/tmp/gta-gateway.sock"
        assert client.default_ipc_mode == "unix"


# ============================================================================
# Test: Connection - HTTP Mode
# ============================================================================

class TestConnectionHTTP:
    """Test HTTP connection mode"""

    @pytest.mark.asyncio
    async def test_connect_http_mode_success(self):
        """Test successful HTTP connection"""
        client = IPCGatewayClient(ipc_mode="http")

        with patch.object(client, '_is_ipc_available', return_value=False):
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_response = Mock()
                mock_response.raise_for_status = Mock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                await client.connect()

                assert client.using_ipc is False
                assert client.client is not None

    @pytest.mark.asyncio
    async def test_connect_http_fallback_when_ipc_unavailable(self):
        """Test HTTP fallback when IPC is unavailable"""
        client = IPCGatewayClient(ipc_mode="auto")

        with patch.object(client, '_is_ipc_available', return_value=False):
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_response = Mock()
                mock_response.raise_for_status = Mock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                await client.connect()

                assert client.using_ipc is False

    @pytest.mark.asyncio
    async def test_connect_health_check_called(self):
        """Test that health check is called on connect"""
        client = IPCGatewayClient(ipc_mode="http")

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            await client.connect()

            # Verify health check was called
            mock_client.get.assert_called_with("/health")

    @pytest.mark.asyncio
    async def test_connect_raises_on_health_check_failure(self):
        """Test connection raises exception when health check fails"""
        client = IPCGatewayClient(ipc_mode="http")

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
            mock_client_class.return_value = mock_client

            with pytest.raises(Exception):
                await client.connect()


# ============================================================================
# Test: IPC Availability Check
# ============================================================================

class TestIPCAvailability:
    """Test IPC availability checking"""

    @patch('platform.system', return_value='Windows')
    def test_ipc_available_windows_always_true(self, mock_platform):
        """Test IPC availability check on Windows returns True"""
        client = IPCGatewayClient()
        # On Windows, we can't easily check if pipe exists, so returns True
        assert client._is_ipc_available() is True

    @patch('platform.system', return_value='Linux')
    @patch('os.path.exists', return_value=False)
    def test_ipc_unavailable_when_socket_missing(self, mock_exists, mock_platform):
        """Test IPC unavailable when socket file doesn't exist"""
        client = IPCGatewayClient()
        assert client._is_ipc_available() is False

    @patch('platform.system', return_value='Linux')
    @patch('os.path.exists', return_value=True)
    @patch('os.stat')
    @patch('stat.S_ISSOCK', return_value=True)
    def test_ipc_available_when_socket_exists(self, mock_issock, mock_stat, mock_exists, mock_platform):
        """Test IPC available when socket file exists"""
        client = IPCGatewayClient()
        mock_stat.return_value = Mock(st_mode=0)
        assert client._is_ipc_available() is True

    @patch('platform.system', return_value='Linux')
    @patch('os.path.exists', side_effect=Exception("Permission denied"))
    def test_ipc_unavailable_on_check_error(self, mock_exists, mock_platform):
        """Test IPC unavailable when check raises exception"""
        client = IPCGatewayClient()
        assert client._is_ipc_available() is False


# ============================================================================
# Test: Get Frames
# ============================================================================

class TestGetFrames:
    """Test fetching frames from Gateway"""

    @pytest.mark.asyncio
    async def test_get_frames_success(self):
        """Test successful frame fetching"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={
            "frames": [
                {"id": 1, "data": "frame1"},
                {"id": 2, "data": "frame2"}
            ]
        })
        mock_client.get = AsyncMock(return_value=mock_response)
        client.client = mock_client

        frames = await client.get_frames()

        assert len(frames) == 2
        assert frames[0]["id"] == 1
        assert frames[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_get_frames_empty_response(self):
        """Test get_frames with 204 No Content"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 204
        mock_client.get = AsyncMock(return_value=mock_response)
        client.client = mock_client

        frames = await client.get_frames()

        assert frames == []

    @pytest.mark.asyncio
    async def test_get_frames_http_error(self):
        """Test get_frames handles HTTP errors"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.get = AsyncMock(side_effect=httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=mock_response
        ))
        client.client = mock_client

        frames = await client.get_frames()

        assert frames == []

    @pytest.mark.asyncio
    async def test_get_frames_network_error(self):
        """Test get_frames handles network errors"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))
        client.client = mock_client

        frames = await client.get_frames()

        assert frames == []

    @pytest.mark.asyncio
    async def test_get_frames_malformed_json(self):
        """Test get_frames handles malformed JSON"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))
        mock_client.get = AsyncMock(return_value=mock_response)
        client.client = mock_client

        frames = await client.get_frames()

        assert frames == []


# ============================================================================
# Test: Get Stats
# ============================================================================

class TestGetStats:
    """Test fetching statistics from Gateway"""

    @pytest.mark.asyncio
    async def test_get_stats_success(self):
        """Test successful stats fetching"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={
            "total_frames": 100,
            "buffer_size": 200
        })
        mock_client.get = AsyncMock(return_value=mock_response)
        client.client = mock_client

        stats = await client.get_stats()

        assert stats["total_frames"] == 100
        assert stats["buffer_size"] == 200

    @pytest.mark.asyncio
    async def test_get_stats_error_returns_empty_dict(self):
        """Test get_stats returns empty dict on error"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Error"))
        client.client = mock_client

        stats = await client.get_stats()

        assert stats == {}


# ============================================================================
# Test: Get Health
# ============================================================================

class TestGetHealth:
    """Test fetching health status from Gateway"""

    @pytest.mark.asyncio
    async def test_get_health_success(self):
        """Test successful health check"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={"status": "healthy"})
        mock_client.get = AsyncMock(return_value=mock_response)
        client.client = mock_client

        health = await client.get_health()

        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_health_error_returns_unhealthy(self):
        """Test get_health returns unhealthy on error"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
        client.client = mock_client

        health = await client.get_health()

        assert health["status"] == "unhealthy"
        assert "error" in health


# ============================================================================
# Test: Close Connection
# ============================================================================

class TestCloseConnection:
    """Test closing client connection"""

    @pytest.mark.asyncio
    async def test_close_when_client_exists(self):
        """Test closing when client exists"""
        client = IPCGatewayClient()

        mock_client = AsyncMock()
        client.client = mock_client

        await client.close()

        mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_when_no_client(self):
        """Test closing when client is None"""
        client = IPCGatewayClient()
        client.client = None

        # Should not raise exception
        await client.close()


# ============================================================================
# Test: Utility Methods
# ============================================================================

class TestUtilityMethods:
    """Test utility methods"""

    def test_is_using_ipc_returns_false_initially(self):
        """Test is_using_ipc returns False initially"""
        client = IPCGatewayClient()
        assert client.is_using_ipc() is False

    def test_is_using_ipc_returns_true_when_using_ipc(self):
        """Test is_using_ipc returns True when IPC is active"""
        client = IPCGatewayClient()
        client.using_ipc = True
        assert client.is_using_ipc() is True


# ============================================================================
# Test: Async Context Manager
# ============================================================================

class TestAsyncContextManager:
    """Test async context manager support"""

    @pytest.mark.asyncio
    async def test_context_manager_connects_and_closes(self):
        """Test context manager calls connect and close"""
        client = IPCGatewayClient(ipc_mode="http")

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            async with client as c:
                assert c is client
                assert client.client is not None

            # Close should have been called
            mock_client.aclose.assert_called_once()


# ============================================================================
# Test: Convenience Function
# ============================================================================

class TestConvenienceFunction:
    """Test create_gateway_client convenience function"""

    @pytest.mark.asyncio
    async def test_create_gateway_client_returns_connected_client(self):
        """Test convenience function returns connected client"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = await create_gateway_client(
                gateway_url="http://localhost:8000",
                ipc_mode="http"
            )

            assert isinstance(client, IPCGatewayClient)
            assert client.client is not None

            await client.close()

    @pytest.mark.asyncio
    async def test_create_gateway_client_with_custom_params(self):
        """Test convenience function with custom parameters"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = await create_gateway_client(
                gateway_url="http://localhost:9000",
                ipc_mode="http"
            )

            assert client.gateway_url == "http://localhost:9000"
            assert client.ipc_mode == "http"

            await client.close()


# ============================================================================
# Test: Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test realistic usage scenarios"""

    @pytest.mark.asyncio
    async def test_complete_workflow_http_mode(self):
        """Test complete workflow in HTTP mode"""
        client = IPCGatewayClient(ipc_mode="http")

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            # Mock responses
            health_response = Mock()
            health_response.raise_for_status = Mock()
            health_response.json = Mock(return_value={"status": "healthy"})

            frames_response = Mock()
            frames_response.status_code = 200
            frames_response.raise_for_status = Mock()
            frames_response.json = Mock(return_value={"frames": [{"id": 1}]})

            stats_response = Mock()
            stats_response.raise_for_status = Mock()
            stats_response.json = Mock(return_value={"total_frames": 10})

            async def mock_get(endpoint):
                if endpoint == "/health":
                    return health_response
                elif endpoint == "/frames":
                    return frames_response
                elif endpoint == "/stats":
                    return stats_response

            mock_client.get = AsyncMock(side_effect=mock_get)
            mock_client_class.return_value = mock_client

            # Connect
            await client.connect()
            assert client.using_ipc is False

            # Get frames
            frames = await client.get_frames()
            assert len(frames) == 1

            # Get stats
            stats = await client.get_stats()
            assert stats["total_frames"] == 10

            # Get health
            health = await client.get_health()
            assert health["status"] == "healthy"

            # Close
            await client.close()

    @pytest.mark.asyncio
    async def test_auto_mode_selection(self):
        """Test auto mode selects appropriate IPC mode"""
        with patch('platform.system', return_value='Linux'):
            client = IPCGatewayClient(ipc_mode="auto")
            assert client.default_ipc_mode == "unix"

        with patch('platform.system', return_value='Windows'):
            client = IPCGatewayClient(ipc_mode="auto")
            assert client.default_ipc_mode == "pipe"
