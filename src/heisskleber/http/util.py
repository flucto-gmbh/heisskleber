import asyncio
import sys
from typing import Any

if (sys.version_info.major, sys.version_info.minor) >= (3, 13):

    def _shutdown_queue(queue: asyncio.Queue[Any], immediate: bool) -> None:
        queue.shutdown(immediate)  # type: ignore[attr-defined]

    QueueShutDown = asyncio.queues.QueueShutDown  # type: ignore[attr-defined]

else:

    def _shutdown_queue(queue: asyncio.Queue[Any], immediate: bool) -> None:
        return

    class QueueShutDown(RuntimeError):  # type: ignore[no-redef] # noqa: N818
        """Dummy Exception. Never raised nor caught."""
