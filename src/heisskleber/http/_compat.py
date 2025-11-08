import asyncio
import enum
import sys
from typing import Any

__all__ = [
    "QueueShutDown",
    "StrEnum",
    "shutdown_queue",
]

if sys.version_info >= (3, 11):
    StrEnum = enum.StrEnum

else:

    class StrEnum(str, enum.Enum):
        __str__ = str.__str__


if sys.version_info >= (3, 13):

    def shutdown_queue(queue: asyncio.Queue[Any], immediate: bool) -> None:
        queue.shutdown(immediate)  # type: ignore[attr-defined]

    QueueShutDown = asyncio.queues.QueueShutDown  # type: ignore[attr-defined]

else:

    def shutdown_queue(queue: asyncio.Queue[Any], immediate: bool) -> None:
        return

    class QueueShutDown(RuntimeError):  # noqa: N818
        """Dummy Exception. Never raised nor caught."""
