import logging
from typing import Any, TypeVar

from heisskleber.core import AsyncSource, Unpacker

from .config import SerialConf

T = TypeVar("T")


class SerialSource(AsyncSource[T]):
    def __init__(self, config: SerialConf, unpack: Unpacker[T]) -> None:
        self.config = config
        self.unpacker = unpack
        self.logger = logging.getLogger("heisskleber")

    async def receive(self) -> tuple[T, dict[str, Any]]:
        raise NotImplementedError

    async def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"SerialSource({self.config.port})"
