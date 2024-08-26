import logging
from typing import Any, TypeVar

from heisskleber.core import AsyncSink, Packer

from .config import SerialConf

T = TypeVar("T")


class SerialSink(AsyncSink[T]):
    def __init__(self, config: SerialConf, pack: Packer[T]) -> None:
        self.config = config
        self.packer = pack
        self.logger = logging.getLogger("heisskleber")

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        pass

    async def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"SerialSink({self.config.port})"
