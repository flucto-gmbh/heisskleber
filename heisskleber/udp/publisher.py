import asyncio
import socket
import sys

from heisskleber.core.packer import get_packer
from heisskleber.core.types import AsyncSink, Serializable, Sink
from heisskleber.udp.config import UdpConf


class UdpPublisher(Sink):
    def __init__(self, config: UdpConf) -> None:
        self.config = config
        self.pack = get_packer(self.config.packer)
        self.is_connected = False

    def start(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as e:
            print(f"failed to create socket: {e}")
            sys.exit(-1)
        else:
            self.is_connected = True

    def stop(self) -> None:
        self.socket.close()
        self.is_connected = True

    def send(self, data: dict[str, Serializable], topic: str | None = None) -> None:
        if not self.is_connected:
            self.start()
        if topic:
            data["topic"] = topic
        payload = self.pack(data).encode("utf-8")
        self.socket.sendto(payload, (self.config.host, self.config.port))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, is_connected: bool) -> None:
        super().__init__()
        self.is_connected = is_connected

    def connection_lost(self, exc: Exception | None) -> None:
        print("Connection lost")
        self.is_connected = False


class AsyncUdpSink(AsyncSink):
    def __init__(self, config: UdpConf) -> None:
        self.config = config
        self.pack = get_packer(self.config.packer)
        self.socket: asyncio.DatagramTransport | None = None
        self.is_connected = False

    def start(self) -> None:
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

    async def send(self, data: dict[str, Serializable], topic: str | None = None) -> None:
        await self._ensure_connection()
        if topic:
            data["topic"] = topic
        payload = self.pack(data).encode(self.config.encoding)
        self.socket.sendto(payload)  # type: ignore

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
