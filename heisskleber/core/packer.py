"""Packer and unpacker for network data."""

import json
from abc import abstractmethod
from typing import Any, Protocol, TypeVar

T_contra = TypeVar("T_contra", contravariant=True)


class Packer(Protocol[T_contra]):
    """Packer Interface.

    This class defines a protocol for packing data.
    It takes data and converts it into a bytes payload.

    Attributes:
        None
    """

    @abstractmethod
    def __call__(self, data: T_contra) -> bytes:
        """Packs the data dictionary into a bytes payload.

        Args:
            data (T_contra): The input data dictionary to be packed.

        Returns:
            bytes: The packed payload.

        Raises:
            TypeError: The data dictionary could not be packed.
        """


class JSONPacker(Packer[dict[str, Any]]):
    """Converts a dictionary into JSON-formatted bytes.

    Args:
        data: A dictionary with string keys and arbitrary values to be serialized into JSON format.

    Returns:
        bytes: The JSON-encoded data as a bytes object.

    Raises:
        TypeError: If the data cannot be serialized to JSON.

    Example:
        >>> packer = JSONPacker()
        >>> result = packer({"key": "value"})
        b'{"key": "value"}'
    """

    def __call__(self, data: dict[str, Any]) -> bytes:  # noqa: D102
        return json.dumps(data).encode()
