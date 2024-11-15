from typing import Any, TypeVar

from heisskleber.core import AsyncSink, Packer, json_packer

T = TypeVar("T")


class ConsoleSink(AsyncSink[T]):
    """Send data to console out."""

    def __init__(
        self,
        pretty: bool = False,
        verbose: bool = False,
        packer: Packer[T] = json_packer,
    ) -> None:
        self.verbose = verbose
        self.pretty = pretty
        self.packer = packer

    async def send(self, data: T, topic: str | None = None, **kwargs: dict[str, Any]) -> None:
        """Serialize data and write to console output."""
        verbose_topic = topic + ":\t" if topic else ""
        serialized = self.packer(data)
        print(verbose_topic + serialized.decode())  # noqa: T201

    def __repr__(self) -> str:
        """Return string reprensentation of ConsoleSink."""
        return f"{self.__class__.__name__}(pretty={self.pretty}, verbose={self.verbose})"

    async def start(self) -> None:
        """Not implemented."""

    def stop(self) -> None:
        """Not implemented."""
