import asyncio
import logging
from typing import Any, TypeVar

from heisskleber.core import AsyncSource, Unpacker, json_unpacker
from heisskleber.udp.config import UdpConf

T = TypeVar("T")


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, is_connected: bool, queue: asyncio.Queue[bytes]) -> None:
        super().__init__()
        self.queue = queue
        self.is_connected = is_connected
        self.logger = logging.getLogger("heisskleber")

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        self.queue.put_nowait(data)

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.logger.info("Connection made")

    def connection_lost(self, exc: Exception | None) -> None:
        self.is_connected = False
        self.logger.info("Connection lost")


class UdpSource(AsyncSource[T]):
    """
    An asynchronous UDP subscriber based on asyncio.protocols.DatagramProtocol
    """

    def __init__(self, config: UdpConf, topic: str = "udp", unpacker: Unpacker[T] = json_unpacker) -> None:
        self.config = config
        self.topic = topic
        self.EOF = self.config.delimiter.encode(self.config.encoding)
        self.unpacker = unpacker
        self.queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=self.config.max_queue_size)
        self.task: asyncio.Task[None] | None = None
        self.is_connected = False
        self.logger = logging.getLogger("heisskleber")

    async def start(self) -> None:
        await self._ensure_connection()

    async def _ensure_connection(self) -> None:
        if not self.is_connected:
            loop = asyncio.get_running_loop()
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: UdpProtocol(self.is_connected, self.queue),
                remote_addr=(self.config.host, self.config.port),
            )

    def stop(self) -> None:
        self.transport.close()

    async def receive(self) -> tuple[T, dict[str, Any]]:
        await self._ensure_connection()

        while True:
            data = None
            try:
                data = await self.queue.get()
                payload, extra = self.unpacker(data)
            except Exception:
                if data:
                    self.logger.warning(f"Could not deserialize data: {data!r}")
            else:
                return (payload, extra)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
