import asyncio
import json
import sys
import time
from queue import SimpleQueue
from threading import Thread

from heisskleber.core.types import AsyncSource, Serializable, Source


class ConsoleSource(Source):
    def __init__(self, topic: str = "console") -> None:
        self.topic = topic
        self.queue = SimpleQueue()
        self.pack = json.loads
        self.thread: Thread | None = None

    def listener_task(self):
        while True:
            try:
                data = sys.stdin.readline()
                payload = self.pack(data)
                self.queue.put(payload)
            except json.decoder.JSONDecodeError:
                print("Invalid JSON")
                continue
            except ValueError:
                break
        print("listener task finished")

    def receive(self) -> tuple[str, dict[str, Serializable]]:
        if not self.thread:
            self.start()

        data = self.queue.get()
        return self.topic, data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(topic={self.topic})"

    def start(self) -> None:
        self.thread = Thread(target=self.listener_task, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if self.thread:
            sys.stdin.close()
            self.thread.join()


class AsyncConsoleSource(AsyncSource):
    def __init__(self, topic: str = "console") -> None:
        self.topic = topic
        self.queue: asyncio.Queue[dict[str, Serializable]] = asyncio.Queue(maxsize=10)
        self.pack = json.loads
        self.task: asyncio.Task[None] | None = None

    async def listener_task(self):
        while True:
            data = sys.stdin.readline()
            payload = self.pack(data)
            await self.queue.put(payload)

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        if not self.task:
            self.start()

        data = await self.queue.get()
        return self.topic, data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(topic={self.topic})"

    def start(self) -> None:
        self.task = asyncio.create_task(self.listener_task())

    def stop(self) -> None:
        if self.task:
            self.task.cancel()


if __name__ == "__main__":
    console_source = ConsoleSource()
    console_source.start()

    print("Listening to console input.")

    count = 0

    try:
        while True:
            print(console_source.receive())
            time.sleep(1)
            count += 1
            print(count)
    except KeyboardInterrupt:
        print("Stopped")
        sys.exit(0)
