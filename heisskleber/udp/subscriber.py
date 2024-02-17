import socket
import sys
import threading
from queue import Queue

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import Serializable, Source
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
