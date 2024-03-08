import asyncio
from typing import Callable

from heisskleber.core.types import AsyncSource, Serializable
from heisskleber.tcp.config import TcpConf


def bytes_csv_unpacker(data: bytes) -> tuple[str, dict[str, str]]:
    vals = data.decode().rstrip().split(",")
    keys = [f"key{i}" for i in range(len(vals))]
    return ("tcp", dict(zip(keys, vals)))


class AsyncTcpSource(AsyncSource):
    """
    Async TCP connection, connects to host:port and reads byte encoded strings.


    Pass an unpack function like so:

    Example
    -------
    def unpack(data: bytes) -> tuple[str, dict[str, float | int | str]]:
        return dict(zip(["key1", "key2"], data.decode().split(","))

    """

    def __init__(self, config: TcpConf, unpack: Callable[[bytes], tuple[str, dict[str, Serializable]]] | None) -> None:
        self.config = config
        self.is_connected = asyncio.Event()
        self.unpack = unpack or bytes_csv_unpacker
        self.timeout = config.timeout
        self.start_task: asyncio.Task[None] | None = None

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        await self._check_connection()
        data = await self.reader.readline()
        topic, payload = self.unpack(data)
        return (topic, payload)  # type: ignore

    def start(self) -> None:
        self.start_task = asyncio.create_task(self._connect())

    def stop(self) -> None:
        if self.is_connected:
            print("stopping")

    async def _check_connection(self) -> None:
        if not self.start_task:
            self.start()
        await self.is_connected.wait()

    async def _connect(self) -> None:
        print(f"{self} waiting for connection.")
        (self.reader, self.writer) = await asyncio.open_connection(self.config.host, self.config.port)
        print(f"{self} connected successfully!")
        self.is_connected.set()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
