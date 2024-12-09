"""Asynchronous sink implementation for sending data via serial port."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

import serial  # type: ignore[import-untyped]

from heisskleber.core import Packer, Sender

from .config import SerialConf

T = TypeVar("T")


class SerialSender(Sender[T]):
    """An asynchronous sink for writing data to a serial port.

    This class implements the AsyncSink interface for writing data to a serial port.
    It uses a thread pool executor to perform blocking I/O operations asynchronously.

    Attributes:
        config: Configuration for the serial port.
        packer: Function to pack data for sending.
    """

    def __init__(self, config: SerialConf, pack: Packer[T]) -> None:
        """SerialSink constructor."""
        self.config = config
        self.packer = pack
        self._loop = asyncio.get_running_loop()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._lock = asyncio.Lock()
        self._is_connected = False
        self._cancel_write_timeout = 1

    async def send(self, data: T, **kwargs: dict[str, Any]) -> None:
        """Send data to the serial port.

        This method packs the data, writes it to the serial port, and then flushes the port.

        Arguments:
            data: The data to be sent.
            **kwargs: Not implemented.

        Raises:
            PackerError: If data could not be packed to bytes with the provided packer.

        Note:
            If the serial port is not connected, it will implicitly attempt to connect first.

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
        """Open serial connection."""
        if hasattr(self, "_ser"):
            return

        self._ser = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.bytesize,
            parity=self.config.parity,
            stopbits=self.config.stopbits,
        )

    async def stop(self) -> None:
        """Close serial connection."""
        self._ser.close()

    def __repr__(self) -> str:
        """Return string representation of SerialSink."""
        return f"SerialSink({self.config.port}, baudrate={self.config.baudrate})"
