"""Packer and unpacker for network data."""

import json
from abc import abstractmethod
from typing import Any, Protocol, TypeVar

T_contra = TypeVar("T_contra", contravariant=True)


class PackerError(Exception):
    """Raised when unpacking operations fail.

    This exception wraps underlying errors that may occur during unpacking,
    providing a consistent interface for error handling.

    Arguments:
        data: The data object that caused the PackerError

    """

    PREVIEW_LENGTH = 100

    def __init__(self, data: Any) -> None:
        """Initialize the error with the failed payload and cause."""
        message = "Failed to pack data."
        super().__init__(message)


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

        Arguments:
            data (T_contra): The input data dictionary to be packed.

        Returns:
            bytes: The packed payload.

        Raises:
            PackerError: The data dictionary could not be packed.

        """


class JSONPacker(Packer[dict[str, Any]]):
    """Converts a dictionary into JSON-formatted bytes.

    Arguments:
        data: A dictionary with string keys and arbitrary values to be serialized into JSON format.

    Returns:
        bytes: The JSON-encoded data as a bytes object.

    Raises:
        PackerError: If the data cannot be serialized to JSON.

    Example:
        >>> packer = JSONPacker()
        >>> result = packer({"key": "value"})
        b'{"key": "value"}'

    """

    def __call__(self, data: dict[str, Any]) -> bytes:
        """Pack the data."""
        try:
            return json.dumps(data).encode()
        except (UnicodeEncodeError, TypeError) as err:
            raise PackerError(data) from err
