import socket
import threading
from queue import SimpleQueue

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import Serializable, Source
from heisskleber.udp.config import UdpConf


class UdpSubscriber(Source):
    def __init__(self, config: UdpConf, topic: str | None = None):
        self.config = config
        self.topic = topic
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.config.ip, self.config.port))
        self.unpacker = get_unpacker(self.config.packer)
        self._queue: SimpleQueue[tuple[str, dict[str, Serializable]]] = SimpleQueue()
        self._running = threading.Event()
        self._running.set()
        self._thread: threading.Thread | None = None

    def receive(self) -> tuple[str, dict[str, Serializable]]:
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

    def start_loop(self) -> None:
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop_loop(self) -> None:
        self._running.clear()
        if self._thread is not None:
            self._thread.join()
        self.socket.close()

    def __del__(self) -> None:
        self.stop_loop()
