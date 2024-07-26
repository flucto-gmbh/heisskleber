"""Packer and unpacker for network data."""

import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Protocol, TypeVar

T = TypeVar("T", contravariant=True)


class Packer(Protocol[T]):
    """Packer Interface.

    This abstract base class defines an interface for packing data.
    It takes a dictionary of data and converts it into a bytes payload.

    Attributes:
        None

    Methods:
        __call__(data: dict[str, Any]) -> bytes:
            Packs the given data dictionary into a bytes payload.
    """

    @abstractmethod
    def __call__(self, data: T) -> bytes:
        """Packs the data dictionary into a bytes payload.

        Args:
            data (dict[str, Any]): The input data dictionary to be packed.

        Returns:
            bytes: The packed payload.

        Raises:
            SerializationError: The data dictionary could not be packed.
        """
        pass


class JSONPacker(Packer[dict[str, Any]]):
    """Default implementation for serialization of json data."""

    def __call__(self, data: dict[str, Any]) -> bytes:
        return json.dumps(data).encode()
