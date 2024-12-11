"""Unpacker protocol definition and example implemetation."""

import json
from abc import abstractmethod
from typing import Any, Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)


class UnpackerError(Exception):
    """Raised when unpacking operations fail.

    This exception wraps underlying errors that may occur during unpacking,
    providing a consistent interface for error handling.

    Arguments:
        payload: The bytes payload that failed to unpack.

    """

    PREVIEW_LENGTH = 100

    def __init__(self, payload: bytes) -> None:
        """Initialize the error with the failed payload and cause."""
        self.payload = payload
        preview = payload[: self.PREVIEW_LENGTH] + b"..." if len(payload) > self.PREVIEW_LENGTH else payload
        message = f"Failed to unpack payload: {preview!r}. "
        super().__init__(message)


class Unpacker(Protocol[T_co]):
    """Unpacker Interface.

    This abstract base class defines an interface for unpacking payloads.
    It takes a payload of bytes, creates a data dictionary and an optional topic,
    and returns a tuple containing the topic and data.
    """

    @abstractmethod
    def __call__(self, payload: bytes) -> tuple[T_co, dict[str, Any]]:
        """Unpacks the payload into a data object and optional meta-data dictionary.

        Args:
            payload (bytes): The input payload to be unpacked.

        Returns:
            tuple[T, Optional[dict[str, Any]]]: A tuple containing:
                - T: The data object generated from the input data, e.g. dict or dataclass
                - dict[str, Any]: The meta data associated with the unpack operation, such as topic, timestamp or errors

        Raises:
            UnpackerError: The payload could not be unpacked.

        """


class JSONUnpacker(Unpacker[dict[str, Any]]):
    """Deserializes JSON-formatted bytes into dictionaries.

    Arguments:
        payload: JSON-formatted bytes to deserialize.

    Returns:
        tuple[dict[str, Any], dict[str, Any]]: A tuple containing:
            - The deserialized JSON data as a dictionary
            - An empty dictionary for metadata (not used in JSON unpacking)

    Raises:
        UnpackerError: If the payload cannot be decoded as valid JSON.

    Example:
        >>> unpacker = JSONUnpacker()
        >>> data, metadata = unpacker(b'{"hotglue": "very_nais"}')
        >>> print(data)
        {'hotglue': 'very_nais'}

    """

    def __call__(self, payload: bytes) -> tuple[dict[str, Any], dict[str, Any]]:
        """Unpack the payload."""
        try:
            return json.loads(payload), {}
        except json.JSONDecodeError as e:
            raise UnpackerError(payload) from e
