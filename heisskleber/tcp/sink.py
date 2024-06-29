"""
Async TCP Sink - send data to arbitrary TCP server
"""
from typing import Any

from heisskleber.config import BaseConf
from heisskleber.core.types import AsyncSink


class AsyncTcpSink(AsyncSink):
    """
    Async TCP Sink
    """

    def __init__(self, config: BaseConf) -> None:
        pass

    async def send(self, data: dict[str, Any], topic: str) -> None:
        pass

    def __repr__(self) -> str:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
