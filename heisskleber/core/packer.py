"""Packer and unpacker for network data."""

import json
from abc import ABC, abstractmethod
from typing import Any


class Unpacker(ABC):
    """Unpacker Interface.

    This abstract base class defines an interface for unpacking payloads.
    It takes a payload of bytes, creates a data dictionary and an optional topic,
    and returns a tuple containing the topic and data.

    Attributes:
        None

    Methods:
        __call__(payload: bytes) -> tuple[str | None, dict[str, Any]]:
            Unpacks the given payload and returns the resulting topic and data.
    """

    @abstractmethod
    def __call__(self, payload: bytes) -> dict[str, Any]:
        """Unpacks the payload into a topic and data dictionary.

        Special treatment will be given to keys that start with an underscore, such as '_topic', which will be used to set the topic.

        Args:
            payload (bytes): The input payload to be unpacked.

        Returns:
            tuple[str | None, dict[str, Any]]: A tuple containing:
                - str | None: The topic extracted from the payload, if any.
                - dict[str, Any]: The data dictionary created from the payload.

        Raises:
            ParserError: The payload could not be unpacked.
        """
        pass


class Packer(ABC):
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
    def __call__(self, data: dict[str, Any]) -> bytes:
        """Packs the data dictionary into a bytes payload.

        Args:
            data (dict[str, Any]): The input data dictionary to be packed.

        Returns:
            bytes: The packed payload.

        Raises:
            SerializationError: The data dictionary could not be packed.
        """
        pass


class JSONUnpacker(Unpacker):
    """Default implementation for deserialzation of json data."""

    def __call__(self, payload: bytes) -> tuple[dict[str, Any], str | None]:
        return json.loads(payload.decode()), None


class JSONPacker(Packer):
    """Default implementation for serialization of json data."""

    def __call__(self, data: dict[str, Any]) -> bytes:
        return json.dumps(data).encode()
