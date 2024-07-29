from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .packer import Packer

T = TypeVar("T")


class AsyncSink(ABC, Generic[T]):
    """
    Sink interface to send() data to.
    """

    packer: Packer[T]

    @abstractmethod
    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        """
        Send data via the implemented output stream.
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

    async def __aenter__(self) -> AsyncSink[T]:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
