"""
Async TCP Sink - send data to arbitrary TCP server
"""

from typing import Any, TypeVar

from heisskleber.core import AsyncSink
from heisskleber.core.packer import Packer

from .config import TcpConf

T = TypeVar("T")


class TcpSink(AsyncSink[T]):
    """
    Async TCP Sink
    """

    def __init__(self, config: TcpConf, pack: Packer[T]) -> None:
        self.config = config

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        pass

    def __repr__(self) -> str:
        return f"TcpSink({self.config.host}:{self.config.port})"

    async def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
