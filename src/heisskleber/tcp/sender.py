from typing import Any, TypeVar

from heisskleber.core import Sender
from heisskleber.core.packer import Packer

from .config import TcpConf

T = TypeVar("T")


class TcpSender(Sender[T]):
    """Async TCP Sink.

    Attributes:
        config: The TcpConf configuration object.
        packer: The packer protocol to serialize data before sending.

    """

    def __init__(self, config: TcpConf, packer: Packer[T]) -> None:
        self.config = config
        self.packer = packer

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        """Send data via tcp connection.

        Arguments:
            data: The data to be sent.
            kwargs: Not implemented.

        """

    def __repr__(self) -> str:
        """Return string representation of TcpSink."""
        return f"TcpSink({self.config.host}:{self.config.port})"

    async def start(self) -> None:
        """Start TcpSink."""

    async def stop(self) -> None:
        """Stop TcpSink."""
