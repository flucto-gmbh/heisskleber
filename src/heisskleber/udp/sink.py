import asyncio
import logging
from typing import Any, TypeVar

from heisskleber.core import AsyncSink, Packer, json_packer
from heisskleber.udp.config import UdpConf

logger = logging.getLogger("heisskleber.udp")

T = TypeVar("T")


class UdpProtocol(asyncio.DatagramProtocol):
    """UDP protocol handler that tracks connection state.

    Arguments:
    ---------
        is_connected: Flag tracking if protocol is connected

    """

    def __init__(self, is_connected: bool) -> None:
        super().__init__()
        self.is_connected = is_connected

    def connection_lost(self, exc: Exception | None) -> None:
        """Update state and log a lost connection."""
        logger.info("UDP Connection lost")
        self.is_connected = False


class UdpSink(AsyncSink[T]):
    """UDP sink for sending data via UDP protocol.

    Arguments:
    ---------
        config: UDP configuration parameters
        packer: Function to serialize data, defaults to JSON packing

    """

    _socket: asyncio.DatagramTransport

    def __init__(self, config: UdpConf, packer: Packer[T] = json_packer) -> None:  # type: ignore[assignment]
        self.config = config
        self.pack = packer
        self.is_connected = False

    async def start(self) -> None:
        """Connect the UdpSink."""
        await self._ensure_connection()

    def stop(self) -> None:
        """Disconnect the UdpSink connection."""
        if self._socket is not None:
            self._socket.close()
        self.is_connected = False

    async def _ensure_connection(self) -> None:
        """Create UDP endpoint if not connected.

        Creates datagram endpoint using protocol handler if no connection exists.
        Updates connected state on successful connection.

        """
        if not self.is_connected:
            loop = asyncio.get_running_loop()
            self._socket, _ = await loop.create_datagram_endpoint(
                lambda: UdpProtocol(self.is_connected),
                remote_addr=(self.config.host, self.config.port),
            )
            self.is_connected = True

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        """Send data over UDP connection.

        Arguments:
        ---------
            data: Data to send
            **kwargs: Additional arguments passed to send

        """
        await self._ensure_connection()
        payload = self.pack(data)
        self._socket.sendto(payload)

    def __repr__(self) -> str:
        """Return string representation of UdpSink."""
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
