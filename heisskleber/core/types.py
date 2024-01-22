from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Union

from heisskleber.config.config import BaseConf

Serializable = Union[str, int, float]


class Sink(ABC):
    """
    Sink interface to send() data to.
    """

    pack: Callable[[dict[str, Serializable]], str]

    @abstractmethod
    def __init__(self, config: BaseConf) -> None:
        """
        Initialize the publisher with a configuration object.
        """
        pass

    @abstractmethod
    def send(self, data: dict[str, Any], topic: str) -> None:
        """
        Send data via the implemented output stream.
        """
        pass


class Source(ABC):
    """
    Source interface that emits data via the receive() method.
    """

    unpack: Callable[[str], dict[str, Serializable]]

    @abstractmethod
    def __init__(self, config: BaseConf, topic: str | list[str]) -> None:
        """
        Initialize the subscriber with a topic and a configuration object.
        """
        pass

    @abstractmethod
    def receive(self) -> tuple[str, dict[str, Serializable]]:
        """
        Blocking function to receive data from the implemented input stream.

        Data is returned as a tuple of (topic, data).
        """
        pass


class AsyncSubscriber(ABC):
    """
    AsyncSubscriber interface
    """

    @abstractmethod
    def __init__(self, config: Any, topic: str | list[str]) -> None:
        """
        Initialize the subscriber with a topic and a configuration object.
        """
        pass

    @abstractmethod
    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        """
        Blocking function to receive data from the implemented input stream.

        Data is returned as a tuple of (topic, data).
        """
        pass


class AsyncSource(ABC):
    """
    AsyncSubscriber interface
    """

    @abstractmethod
    def __init__(self, config: Any, topic: str | list[str]) -> None:
        """
        Initialize the subscriber with a topic and a configuration object.
        """
        pass

    @abstractmethod
    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        """
        Blocking function to receive data from the implemented input stream.

        Data is returned as a tuple of (topic, data).
        """
        pass


class AsyncSink(ABC):
    """
    Sink interface to send() data to.
    """

    pack: Callable[[dict[str, Serializable]], str]

    @abstractmethod
    def __init__(self, config: BaseConf) -> None:
        """
        Initialize the publisher with a configuration object.
        """
        pass

    @abstractmethod
    async def send(self, data: dict[str, Any], topic: str) -> None:
        """
        Send data via the implemented output stream.
        """
        pass
