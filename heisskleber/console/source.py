import json
import sys
import time
from queue import SimpleQueue
from threading import Thread

from heisskleber.core.types import Serializable, Source


class ConsoleSource(Source):
    def __init__(self, topic: str | list[str] | tuple[str] = "console") -> None:
        self.topic = "console"
        self.queue = SimpleQueue()
        self.listener_daemon = Thread(target=self.listener_task, daemon=True)
        self.listener_daemon.start()
        self.pack = json.loads

    def listener_task(self):
        while True:
            data = sys.stdin.readline()
            payload = self.pack(data)
            self.queue.put(payload)

    def receive(self) -> tuple[str, dict[str, Serializable]]:
        data = self.queue.get()
        return self.topic, data


if __name__ == "__main__":
    console_source = ConsoleSource()

    while True:
        print(console_source.receive())
        time.sleep(1)
