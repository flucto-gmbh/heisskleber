"""Asynchronous data source interface."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Generic

from .unpacker import T_co, Unpacker


class Receiver(ABC, Generic[T_co]):
    """Abstract interface for asynchronous data sources.

    This class defines a protocol for receiving data from various input streams
    asynchronously. It supports both async iteration and context manager patterns,
    and ensures proper resource management.

    The source is covariant in its type parameter, allowing for type-safe subtyping
    relationships.

    Attributes:
        unpacker: Component responsible for deserializing incoming data into type T_co.

    Example:
        >>> async with CustomSource(unpacker) as source:
        ...     async for data, metadata in source:
        ...         print(f"Received: {data}, metadata: {metadata}")

    """

    unpacker: Unpacker[T_co]

    @abstractmethod
    async def receive(self, **kwargs: Any) -> tuple[T_co, dict[str, Any]]:
        """Receive data from the implemented input stream.

        Returns:
            tuple[T_co, dict[str, Any]]: A tuple containing:
                - The received and unpacked data of type T_co
                - A dictionary of metadata associated with the received data

        Raises:
            Any implementation-specific exceptions that might occur during receiving.

        """

    @abstractmethod
    async def start(self) -> None:
        """Initialize and start any background processes and tasks of the source."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop any background processes and tasks."""

    @abstractmethod
    def __repr__(self) -> str:
        """A string reprensatiion of the source."""

    def __aiter__(self) -> "Receiver[T_co]":
        """Return self as the async iterator object.

        This method enables the receiver to be used in async for loops.

        Returns:
            Self as the async iterator.
        """
        return self

    async def __anext__(self) -> tuple[T_co, dict[str, Any]]:
        """Get the next item from the receiver's data stream.

        This method implements async iteration by calling the receive() method
        and returning its result.

        Returns:
            tuple[T_co, dict[str, Any]]: The next data item and its associated
                metadata as returned by receive().

        Raises:
            StopAsyncIteration: When the receiver has no more data.
            Any other exceptions that might occur during receive().
        """
        data, meta = await self.receive()
        return data, meta

    async def __aenter__(self) -> "Receiver[T_co]":
        """Initialize the source for use in an async context manager.

        Returns:
            AsyncSource[T_co]: The initialized source instance.

        Raises:
            Any exceptions that might occur during start().

        """
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Cleanup the source when exiting an async context manager.

        Arguments:
            exc_type: The type of the exception that was raised, if any.
            exc_value: The instance of the exception that was raised, if any.
            traceback: The traceback of the exception that was raised, if any.

        """
        await self.stop()
