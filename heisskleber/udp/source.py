import asyncio
import logging
from typing import Any, TypeVar

from heisskleber.core import AsyncSource, Unpacker, json_unpacker
from heisskleber.udp.config import UdpConf

T = TypeVar("T")


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, queue: asyncio.Queue[bytes]) -> None:
        super().__init__()
        self.queue = queue

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        self.queue.put_nowait(data)

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        print("Connection made")


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
        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(self.queue),
            local_addr=(self.config.host, self.config.port),
        )
        self.is_connected = True
        print("Udp connection established.")

    def stop(self) -> None:
        self.transport.close()

    async def receive(self) -> tuple[T, dict[str, Any]]:
        if not self.is_connected:
            await self.start()

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
