from typing import Any, TypeVar

from heisskleber.core import Packer, Sender, json_packer

T = TypeVar("T")


class ConsoleSender(Sender[T]):
    """Send data to console out."""

    def __init__(
        self,
        pretty: bool = False,
        verbose: bool = False,
        packer: Packer[T] = json_packer,  # type: ignore[assignment]
    ) -> None:
        self.verbose = verbose
        self.pretty = pretty
        self.packer = packer

    async def send(self, data: T, topic: str | None = None, **kwargs: dict[str, Any]) -> None:
        """Serialize data and write to console output."""
        serialized = self.packer(data)
        output = f"{topic}:\t{serialized.decode()}" if topic else serialized.decode()
        print(output)  # noqa: T201

    def __repr__(self) -> str:
        """Return string reprensentation of ConsoleSink."""
        return f"{self.__class__.__name__}(pretty={self.pretty}, verbose={self.verbose})"

    async def start(self) -> None:
        """Not implemented."""

    async def stop(self) -> None:
        """Not implemented."""
