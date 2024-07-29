import asyncio
from typing import Any, TypeVar

from heisskleber.core import AsyncSink, json_packer
from heisskleber.core.packer import Packer
from heisskleber.udp.config import UdpConf

T = TypeVar("T")


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, is_connected: bool) -> None:
        super().__init__()
        self.is_connected = is_connected

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        print("Connection made")

    def connection_lost(self, exc: Exception | None) -> None:
        print("Connection lost")
        self.is_connected = False


class UdpSink(AsyncSink[T]):
    def __init__(self, config: UdpConf, packer: Packer[T] = json_packer) -> None:
        self.config = config
        self.pack = packer
        self.socket: asyncio.DatagramTransport | None = None
        self.is_connected = False

    async def start(self) -> None:
        # No background loop required
        pass

    def stop(self) -> None:
        if self.socket is not None:
            self.socket.close()
        self.is_connected = False

    async def _ensure_connection(self) -> None:
        if not self.is_connected:
            loop = asyncio.get_running_loop()
            self.socket, _ = await loop.create_datagram_endpoint(
                lambda: UdpProtocol(self.is_connected),
                remote_addr=(self.config.host, self.config.port),
            )
            self.is_connected = True

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        await self._ensure_connection()
        payload = self.pack(data)
        self.socket.sendto(payload)  # type: ignore

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
