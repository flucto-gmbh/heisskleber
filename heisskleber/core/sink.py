from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .packer import Packer

T = TypeVar("T")
# E = TypeVar("E", bound=dict[str, Any])
E = TypeVar("E")


class AsyncSink(ABC, Generic[T, E]):
    """
    Sink interface to send() data to.
    """

    packer: Packer[T]

    @abstractmethod
    async def send(self, data: T, extra: E) -> None:
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
