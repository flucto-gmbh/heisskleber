import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

import serial

from heisskleber.core import AsyncSink, Packer

from .config import SerialConf

T = TypeVar("T")


class SerialSink(AsyncSink[T]):
    """
    An asynchronous sink for writing data to a serial port.

    This class implements the AsyncSink interface for writing data to a serial port.
    It uses a thread pool executor to perform blocking I/O operations asynchronously.

    Attributes:
        config (SerialConf): Configuration for the serial port.
        packer (Packer[T]): Function to pack data for sending.
    """

    def __init__(self, config: SerialConf, pack: Packer[T]) -> None:
        self.config = config
        self.packer = pack
        self._loop = asyncio.get_running_loop()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._lock = asyncio.Lock()
        self._is_connected = False
        self._cancel_write_timeout = 1

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        """
        Send data to the serial port.

        This method packs the data, writes it to the serial port, and then flushes the port.
        If the serial port is not connected, it will attempt to connect first.

        Args:
            data (T): The data to be sent.
            **kwargs: Additional keyword arguments (unused in this implementation).
        """
        if not self._is_connected:
            await self.start()

        payload = self.packer(data)
        try:
            await asyncio.get_running_loop().run_in_executor(self._executor, self._ser.write, payload)
            await asyncio.get_running_loop().run_in_executor(self._executor, self._ser.flush)

        except asyncio.CancelledError:
            await asyncio.shield(self._cancel_write())
            raise

    async def _cancel_write(self) -> None:
        if not hasattr(self, "_ser"):
            return
        await asyncio.wait_for(
            asyncio.get_running_loop().run_in_executor(self._executor, self._ser.cancel_write),
            self._cancel_write_timeout,
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
        return f"SerialSink({self.config.port}, baudrate={self.config.baudrate})"
