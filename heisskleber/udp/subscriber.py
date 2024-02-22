import asyncio
import socket
import sys
import threading
from queue import Queue
from typing import Any

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import AsyncSource, Serializable, Source
from heisskleber.udp.config import UdpConf


class UdpSubscriber(Source):
    def __init__(self, config: UdpConf, topic: str | None = None):
        self.config = config
        self.topic = topic
        self.unpacker = get_unpacker(self.config.packer)
        self._queue: Queue[tuple[str, dict[str, Serializable]]] = Queue(maxsize=self.config.max_queue_size)
        self._running = threading.Event()

    def start(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as e:
            print(f"failed to create socket: {e}")
            sys.exit(-1)
        self.socket.bind((self.config.host, self.config.port))
        self._running.set()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        # if self._thread is not None:
        #     self._thread.join()
        self.socket.close()

    def receive(self) -> tuple[str, dict[str, Serializable]]:
        if not self._running.is_set():
            self.start()
        return self._queue.get()

    def _loop(self) -> None:
        while self._running.is_set():
            try:
                payload, _ = self.socket.recvfrom(1024)
                data = self.unpacker(payload.decode("utf-8"))
                topic: str = str(data.pop("topic")) if "topic" in data else ""
                self._queue.put((topic, data))
            except Exception as e:
                error_message = f"Error in UDP listener loop: {e}"
                print(error_message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(self, queue: asyncio.Queue[bytes]) -> None:
        super().__init__()
        self.queue = queue

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        self.queue.put_nowait(data)


class AsyncUdpSubscriber(AsyncSource):
    """
    An asynchronous UDP subscriber based on asyncio.protocols.DatagramProtocol
    """

    def __init__(self, config: UdpConf, topic: str = "udp"):
        self.config = config
        self.topic = topic
        self.unpacker = get_unpacker(self.config.packer)
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

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self.transport.close()

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        if not self.is_connected:
            await self.setup()

        data = await self.queue.get()
        try:
            payload = self.unpacker(data.decode(self.config.encoding))
        except UnicodeDecodeError:
            print(f"Could not decode data, is not {self.config.encoding}")
            sys.exit(-1)
        except Exception:
            print(f"Could not deserialize data: {data!r}")
            sys.exit(-1)
        return (self.topic, payload)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
