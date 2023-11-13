from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Union

Serializable = Union[str, int, float]


class Publisher(ABC):
    """
    Publisher interface.
    """

    pack: Callable[[dict[str, Serializable]], str]

    @abstractmethod
    def __init__(self, config: Any) -> None:
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


class Subscriber(ABC):
    """
    Subscriber interface
    """

    unpack: Callable[[str], dict[str, Serializable]]

    @abstractmethod
    def __init__(self, config: Any, topic: str | list[str]) -> None:
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

    @abstractmethod
    def run(self) -> None:
        """
        Run the subscriber loop.
        """
        pass
