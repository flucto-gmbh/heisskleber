import asyncio
import json
import sys
from typing import Any, Callable

from heisskleber.core import AsyncSource


def string_to_json(payload: str) -> tuple[dict[str, Any], str | None]:
    return json.loads(payload), None


class AsyncConsoleSource(AsyncSource[dict[str, Any]]):
    def __init__(
        self,
        topic: str = "console",
        unpacker: Callable[[str], tuple[dict[str, Any], str | None]] = string_to_json,
    ) -> None:
        self.topic = topic
        self.queue: asyncio.Queue[tuple[dict[str, Any], str | None]] = asyncio.Queue(maxsize=10)
        self.unpack = unpacker
        self.task: asyncio.Task[None] | None = None

    async def listener_task(self) -> None:
        while True:
            payload = sys.stdin.readline()
            data, topic = self.unpack(payload)
            await self.queue.put((data, topic))

    async def receive(self) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.task:
            self.task = asyncio.create_task(self.listener_task())

        data, topic = await self.queue.get()
        topic = topic or self.topic
        return data, {"topic": topic}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(topic={self.topic})"

    async def start(self) -> None:
        self.task = asyncio.create_task(self.listener_task())

    def stop(self) -> None:
        if self.task:
            self.task.cancel()
