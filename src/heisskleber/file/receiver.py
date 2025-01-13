import asyncio
import logging
from typing import Any, TypeVar

from heisskleber.core import Receiver, Unpacker, json_unpacker
from heisskleber.core.utils import retry
from heisskleber.file.config import FileConf

T = TypeVar("T")
logger = logging.getLogger("heisskleber.mqtt")


class FileReceiver(Receiver[T]):
    """Asynchronous File Reader based on aiofiles."""

    def __init__(
        self,
        config: FileConf,
        unpacker: Unpacker[T] = json_unpacker,  # type: ignore[assignment]
    ) -> None:
        self.config = config
        self.unpacker = unpacker

    async def receive(self) -> tuple[T, dict[str, Any]]:
        # data, extra = self.unpacker()
        # return (data, extra)
        pass

    def __repr__(self) -> str:
        """Return string representation of Mqtt Source class."""
        return f"{self.__class__.__name__}()"

    async def start(self) -> None:
        """Open the file reader listener task."""

    async def stop(self) -> None:
        """Stop the file reader."""
