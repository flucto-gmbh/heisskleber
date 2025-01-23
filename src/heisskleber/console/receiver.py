import asyncio
import sys
from typing import Any, TypeVar

from heisskleber.core import Receiver, Unpacker, json_unpacker

from .config import ConsoleConf

T = TypeVar("T")


class ConsoleReceiver(Receiver[T]):
    """Read stdin from console and create data of type T."""

    def __init__(
        self,
        config: ConsoleConf,
        unpacker: Unpacker[T] = json_unpacker,  # type: ignore[assignment]
    ) -> None:
        self.queue: asyncio.Queue[tuple[T, dict[str, Any]]] = asyncio.Queue(maxsize=10)
        self.unpacker = unpacker
        self.config = config
        self.task: asyncio.Task[None] | None = None

    async def _listener_task(self) -> None:
        while True:
            payload = sys.stdin.readline().encode()  # I know this is stupid, but I adhere to the interface for now
            data, extra = self.unpacker(payload)
            await self.queue.put((data, extra))

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Receive the next message from the console input."""
        if not self.task:
            self.task = asyncio.create_task(self._listener_task())

        data, extra = await self.queue.get()
        return data, extra

    def __repr__(self) -> str:
        """Return string representation of ConsoleSource."""
        return f"{self.__class__.__name__}"

    async def start(self) -> None:
        """Start ConsoleSource."""
        self.task = asyncio.create_task(self._listener_task())

    async def stop(self) -> None:
        """Stop ConsoleSource."""
        if self.task:
            self.task.cancel()
