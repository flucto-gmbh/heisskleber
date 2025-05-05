import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from heisskleber.udp.config import UdpConf
from heisskleber.udp.sender import UdpProtocol, UdpSender


@pytest.fixture
def udp_config():
    """Fixture providing basic UDP configuration."""
    return UdpConf(host="127.0.0.1", port=54321)


@pytest.fixture
def mock_transport():
    """Fixture providing a mock transport."""
    transport = MagicMock(spec=asyncio.DatagramTransport)
    transport.is_closing.return_value = False
    return transport


@pytest.fixture
def udp_sink(udp_config):
    """Fixture providing a UDP sink instance."""
    return UdpSender(udp_config)


@pytest.mark.asyncio
class TestUdpSink:
    """Test suite for UdpSink class."""

    async def test_init(self, udp_sink, udp_config):
        """Test initialization of UdpSink."""
        assert udp_sink.config == udp_config
        assert not udp_sink.is_connected
        assert callable(udp_sink.pack)

    @patch("asyncio.get_running_loop")
    async def test_ensure_connection(self, mock_get_loop, udp_sink, mock_transport):
        """Test connection establishment."""
        mock_loop = AsyncMock()
        mock_loop.create_datagram_endpoint.return_value = (mock_transport, None)
        mock_get_loop.return_value = mock_loop

        await udp_sink._ensure_connection()

        mock_loop.create_datagram_endpoint.assert_called_once()
        assert udp_sink.is_connected
        assert udp_sink._transport == mock_transport

    @patch("asyncio.get_running_loop")
    async def test_ensure_connection_already_connected(self, mock_get_loop, udp_sink, mock_transport):
        """Test that _ensure_connection doesn't reconnect if already connected."""
        mock_loop = AsyncMock()
        mock_get_loop.return_value = mock_loop
        udp_sink.is_connected = True
        udp_sink._transport = mock_transport

        await udp_sink._ensure_connection()

        mock_loop.create_datagram_endpoint.assert_not_called()

    async def test_stop(self, udp_sink, mock_transport):
        """Test stopping the UDP sink."""
        udp_sink.is_connected = True
        udp_sink._transport = mock_transport

        await udp_sink.stop()

        mock_transport.close.assert_called_once()
        assert not udp_sink.is_connected

    async def test_stop_not_connected(self, udp_sink: UdpSender) -> None:
        """Test stopping when not connected."""
        await udp_sink.stop()
        assert not udp_sink.is_connected

    @patch("asyncio.get_running_loop")
    async def test_send(self, mock_get_loop, udp_sink, mock_transport):
        """Test sending data through UDP sink."""
        mock_loop = AsyncMock()
        mock_loop.create_datagram_endpoint.return_value = (mock_transport, None)
        mock_get_loop.return_value = mock_loop

        test_data = {"test": "data"}
        await udp_sink.send(test_data)

        expected_payload = json.dumps(test_data).encode()
        mock_transport.sendto.assert_called_once_with(expected_payload)

    @patch("asyncio.get_running_loop")
    async def test_send_custom_packer(self, mock_get_loop, udp_config, mock_transport):
        """Test sending data with custom packer."""

        def custom_packer(data: dict) -> bytes:
            return b"custom_packed_data"

        sink = UdpSender(udp_config, packer=custom_packer)
        mock_loop = AsyncMock()
        mock_loop.create_datagram_endpoint.return_value = (mock_transport, None)
        mock_get_loop.return_value = mock_loop

        test_data = {"test": "data"}
        await sink.send(test_data)

        mock_transport.sendto.assert_called_once_with(b"custom_packed_data")
        await sink.stop()


class TestUdpProtocol:
    """Test suite for UdpProtocol class."""

    def test_init(self):
        """Test initialization of UdpProtocol."""
        protocol = UdpProtocol(is_connected=True)
        assert protocol.is_connected

    def test_connection_lost(self):
        """Test connection lost handler."""
        protocol = UdpProtocol(is_connected=True)
        protocol.connection_lost(None)
        assert not protocol.is_connected

    def test_connection_lost_with_exception(self):
        """Test connection lost handler with exception."""
        protocol = UdpProtocol(is_connected=True)
        test_exception = Exception("Test exception")
        protocol.connection_lost(test_exception)
        assert not protocol.is_connected
