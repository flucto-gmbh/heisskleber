import asyncio
from typing import Any

from heisskleber.core.packer import JSONUnpacker, Unpacker
from heisskleber.core.types import AsyncSource
from heisskleber.udp.config import UdpConf

default_unpacker = JSONUnpacker()


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, queue: asyncio.Queue[bytes]) -> None:
        super().__init__()
        self.queue = queue

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        self.queue.put_nowait(data)

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        print("Connection made")


class AsyncUdpSource(AsyncSource):
    """
    An asynchronous UDP subscriber based on asyncio.protocols.DatagramProtocol
    """

    def __init__(self, config: UdpConf, topic: str = "udp", unpacker: Unpacker = default_unpacker) -> None:
        self.config = config
        self.topic = topic
        self.EOF = self.config.delimiter.encode(self.config.encoding)
        self.unpacker = unpacker
        self.queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=self.config.max_queue_size)
        self.task: asyncio.Task[None] | None = None
        self.is_connected = False

    async def setup(self) -> None:
        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(self.queue),
            local_addr=(self.config.host, self.config.port),
        )
        self.is_connected = True
        print("Udp connection established.")

    def start(self) -> None:
        # Background loop not required, handled by Protocol
        pass

    def stop(self) -> None:
        self.transport.close()

    async def receive(self) -> tuple[str, dict[str, Any]]:
        if not self.is_connected:
            await self.setup()
        data = await self.queue.get()
        try:
            topic, payload = self.unpacker(data)
        # except UnicodeDecodeError: # this won't be thrown anymore, as the error flag is set to ignore!
        #     print(f"Could not decode data, is not {self.config.encoding}")
        except Exception:
            if self.config.verbose:
                print(f"Could not deserialize data: {data!r}")
        else:
            return (self.topic, payload)

        return await self.receive()  # Try again

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
