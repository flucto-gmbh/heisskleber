import json
from typing import Any, TypeVar

from heisskleber.core import Packer, Sender

from .config import ConsoleConf

T = TypeVar("T")


class ConsoleSender(Sender[T]):
    """Send data to console out."""

    def __init__(
        self,
        config: ConsoleConf,
        packer: Packer[T] = lambda x: json.dumps(x),  # type: ignore[assignment]
    ) -> None:
        self.verbose = config.verbose
        self.pretty = config.pretty
        self.packer = packer

    async def send(self, data: T, topic: str | None = None, **kwargs: dict[str, Any]) -> None:
        """Serialize data and write to console output."""
        serialized = self.packer(data)
        serialized = serialized.decode() if isinstance(serialized, bytes | bytearray) else serialized
        output = f"{topic}:\t{serialized}" if topic else serialized
        print(output)  # noqa: T201

    def __repr__(self) -> str:
        """Return string reprensentation of ConsoleSink."""
        return f"{self.__class__.__name__}(pretty={self.pretty}, verbose={self.verbose})"

    async def start(self) -> None:
        """Not implemented."""

    async def stop(self) -> None:
        """Not implemented."""
