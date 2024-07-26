from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Generic

from heisskleber.config import BaseConf

from .packer import Packer, T, Unpacker


class AsyncSource(ABC, Generic[T]):
    """
    AsyncSubscriber interface
    """

    unpacker: Unpacker

    async def __aiter__(self) -> AsyncGenerator[tuple[T, dict[str, Any]], None]:
        while True:
            data, meta = await self.receive()
            yield data, meta

    @abstractmethod
    def __init__(self, config: BaseConf, topic: str | list[str]) -> None:
        """
        Initialize the subscriber with a topic and a configuration object.
        """
        pass

    @abstractmethod
    async def receive(self) -> tuple[T, dict[str, Any]]:
        """
        Blocking function to receive data from the implemented input stream.

        Data is returned as a tuple of (topic, data).
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def start(self) -> None:
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


class AsyncSink(ABC, Generic[T]):
    """
    Sink interface to send() data to.
    """

    packer: Packer

    @abstractmethod
    def __init__(self, config: BaseConf) -> None:
        """
        Initialize the publisher with a configuration object.
        """
        pass

    @abstractmethod
    async def send(self, data: dict[str, T], topic: str) -> None:
        """
        Send data via the implemented output stream.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def start(self) -> None:
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
