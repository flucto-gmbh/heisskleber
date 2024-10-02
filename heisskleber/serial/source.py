import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

import serial

from heisskleber.core import AsyncSource, Unpacker

from .config import SerialConf

T = TypeVar("T")
logger = logging.getLogger(__name__)


class SerialSource(AsyncSource[T]):
    def __init__(self, config: SerialConf, unpack: Unpacker[T]) -> None:
        self.config = config
        self.unpacker = unpack
        self.logger = logging.getLogger("heisskleber")
        self._loop = asyncio.get_running_loop()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._lock = asyncio.Lock()
        self._is_connected = False
        self._cancel_read_timeout = 1

    async def receive(self) -> tuple[T, dict[str, Any]]:
        if not self._is_connected:
            await self.start()

        try:
            payload = await asyncio.get_running_loop().run_in_executor(self._executor, self._ser.readline, -1)
        except asyncio.CancelledError:
            await asyncio.shield(self._cancel_read())
            raise

        data, extra = self.unpacker(payload=payload)
        logger.debug(f"SerialSource{self.config.port}: Unpacked payload: {data}, extra information: {extra}")
        return (data, extra)

    async def _cancel_read(self) -> None:
        if not hasattr(self, "_ser"):
            return
        logger.warning(f"SerialSource({self.config.port}).read() cancelled, waiting for {self._cancel_read_timeout}.")
        await asyncio.wait_for(
            asyncio.get_running_loop().run_in_executor(self._executor, self._ser.cancel_read), self._cancel_read_timeout
        )

    async def start(self) -> None:
        if hasattr(self, "_ser"):
            return

        self._ser = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.bytesize,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )

    def stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"SerialSource({self.config.port})"
