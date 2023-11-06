from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Union

PayloadType = Union[str, int, float]


class Publisher(ABC):
    """
    Publisher interface.
    """

    pack: Callable[[dict[str, Any] | Any], str]

    @abstractmethod
    def __init__(self, config: Any) -> None:
        """
        Initialize the publisher with a configuration object.
        """
        pass

    @abstractmethod
    def send(self, topic: str, data: dict[str, Any]) -> None:
        """
        Send data via the implemented output stream.
        """
        pass


class Subscriber(ABC):
    """
    Subscriber interface
    """

    unpack: Callable[[bytes], dict[str, PayloadType] | Any]

    @abstractmethod
    def __init__(self, topic: str | list[str], config: Any) -> None:
        """
        Initialize the subscriber with a topic and a configuration object.
        """
        pass

    @abstractmethod
    def receive(self) -> tuple[str, dict[str, PayloadType]]:
        """
        Blocking function to receive data from the implemented input stream.

        Data is returned as a tuple of (topic, data).
        """
        pass
