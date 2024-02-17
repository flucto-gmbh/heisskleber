from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Union

from heisskleber.config import BaseConf

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
    def send(self, data: dict[str, Serializable], topic: str) -> None:
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
