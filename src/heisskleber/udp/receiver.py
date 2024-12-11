import asyncio
import logging
from typing import Any, TypeVar

from heisskleber.core import Receiver, Unpacker, json_unpacker
from heisskleber.udp.config import UdpConf

logger = logging.getLogger("heisskleber.udp")
T = TypeVar("T")


class UdpProtocol(asyncio.DatagramProtocol):
    """Protocol for udp connection.

    Arguments:
        queue: The asyncioQueue to put messages into.

    """

    def __init__(self, queue: asyncio.Queue[bytes]) -> None:
        super().__init__()
        self.queue = queue

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        """Handle received udp message."""
        self.queue.put_nowait(data)

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:  # type: ignore[override]
        """Log successful connection."""
        logger.info("UdpSource: Connection made")


class UdpReceiver(Receiver[T]):
    """An asynchronous UDP subscriber based on asyncio.protocols.DatagramProtocol."""

    def __init__(self, config: UdpConf, unpacker: Unpacker[T] = json_unpacker) -> None:  # type: ignore[assignment]
        self.config = config
        self.EOF = self.config.delimiter.encode(self.config.encoding)
        self.unpacker = unpacker
        self._queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=self.config.max_queue_size)
        self._task: asyncio.Task[None] | None = None
        self._is_connected = False
        self._transport: asyncio.DatagramTransport | None = None
        self._protocol: asyncio.DatagramProtocol | None = None

    async def start(self) -> None:
        """Start udp connection."""
        loop = asyncio.get_event_loop()
        self._transport, self._protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(self._queue),
            local_addr=(self.config.host, self.config.port),
        )
        self._is_connected = True
        logger.info("Udp connection established.")

    async def stop(self) -> None:
        """Stop the udp connection."""
        if self._transport is not None:
            self._transport.close()
            self._transport = None
        self._is_connected = False

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Get the next message from the udp connection.

        Returns:
            tuple[T, dict[str, Any]]
                - The data as returned by the unpacker.
                - A dictionary containing extra information.

        Raises:
            UnpackerError: If the received message could not be unpacked.

        """
        if not self._is_connected:
            await self.start()

        while True:
            data = None
            data = await self._queue.get()
            payload, extra = self.unpacker(data)
            return (payload, extra)

    def __repr__(self) -> str:
        """Return string representation of UdpSource."""
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
