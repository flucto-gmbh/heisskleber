"""Asyncronous data sink interface."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Generic, TypeVar

from .packer import Packer

T = TypeVar("T")


class AsyncSink(ABC, Generic[T]):
    """Abstract interface for asynchronous data sinks.

    This class defines a protocol for sending data to various output streams
    asynchronously. It supports context manager usage and ensures proper
    resource management.

    Attributes:
        packer: Component responsible for serializing type T data before sending.
    """

    packer: Packer[T]

    @abstractmethod
    async def send(self, data: T, **kwargs: Any) -> None:
        """Send data through the implemented output stream.

        Args:
            data: The data to be sent, of type T.
            **kwargs: Additional implementation-specific arguments.
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """Initialize and start the sink's background processes and tasks."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop and cleanup the sink's background processes and tasks.

        This method should be called when the sink is no longer needed.
        It should handle cleanup of any resources initialized in start().
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """A string representation of the sink."""
        pass

    async def __aenter__(self) -> "AsyncSink[T]":
        """Initialize the sink for use in an async context manager.

        Returns:
            AsyncSink[T]: The initialized sink instance.

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
        """Cleanup the sink when exiting an async context manager.

        Args:
            exc_type: The type of the exception that was raised, if any.
            exc_value: The instance of the exception that was raised, if any.
            traceback: The traceback of the exception that was raised, if any.
        """
        self.stop()
