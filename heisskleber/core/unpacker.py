"""Packer and unpacker for network data."""

import json
from abc import abstractmethod
from typing import Any, Protocol, TypeVar

T = TypeVar("T", contravariant=True)


class Unpacker(Protocol[T]):
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
    def __call__(self, payload: bytes) -> tuple[T, dict[str, Any]]:
        """Unpacks the payload into a data object and optional meta-data dictionary

        Args:
            payload (bytes): The input payload to be unpacked.

        Returns:
            tuple[T, Optional[dict[str, Any]]]: A tuple containing:
                - T: The data object generated from the input data, e.g. dict or dataclass
                - dict[str, Any]: The meta data associated with the unpack operation, such as topic, timestamp or errors

        Raises:
            ParserError: The payload could not be unpacked.
        """
        pass


class JSONUnpacker(Unpacker):
    """Default implementation for deserialzation of json data.

    Args:
        payload (bytes): The input payload to be unpacked.

    Returns:
        tuple[dict[str, Any], dict[str, Any]]]: A tuple containing:
            - T: The data object generated from the input data, e.g. dict or dataclass
            - dict[str, Any]: The meta data associated with the unpack operation, such as topic, timestamp or errors
    """

    def __call__(self, payload: bytes) -> tuple[dict[str, Any], dict[str, Any]]:
        return json.loads(payload.decode()), {}
