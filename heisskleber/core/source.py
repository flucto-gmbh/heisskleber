from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Generic

from .unpacker import T, Unpacker


class AsyncSource(ABC, Generic[T]):
    """
    Asyncronous data source interface
    """

    unpacker: Unpacker[T]

    @abstractmethod
    async def receive(self) -> tuple[T, dict[str, Any]]:
        """
        Receive data from the implemented input stream.

        Data is returned as a tuple of (data, extra), where extra contains meta-data.
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        Start any background processes and tasks.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop any background processes and tasks.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    async def __aiter__(self) -> AsyncGenerator[tuple[T, dict[str, Any]], None]:
        while True:
            data, meta = await self.receive()
            yield data, meta

    async def __aenter__(self) -> AsyncSource[T]:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
