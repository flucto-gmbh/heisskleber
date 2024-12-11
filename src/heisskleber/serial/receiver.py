import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

import serial  # type: ignore[import-untyped]

from heisskleber.core import Receiver, Unpacker

from .config import SerialConf

T = TypeVar("T")
logger = logging.getLogger("heisskleber.serial")


class SerialReceiver(Receiver[T]):
    """An asynchronous source for reading data from a serial port.

    This class implements the AsyncSource interface for reading data from a serial port.
    It uses a thread pool executor to perform blocking I/O operations asynchronously.

    Attributes:
        config: Configuration for the serial port.
        unpacker: Function to unpack received data.

    """

    def __init__(self, config: SerialConf, unpack: Unpacker[T]) -> None:
        self.config = config
        self.unpacker = unpack
        self._loop = asyncio.get_running_loop()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._lock = asyncio.Lock()
        self._is_connected = False
        self._cancel_read_timeout = 1

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Receive data from the serial port.

        This method reads a line from the serial port, unpacks it, and returns the data.
        If the serial port is not connected, it will attempt to connect first.

        Returns:
            tuple[T, dict[str, Any]]: A tuple containing the unpacked data and any extra information.

        Raises:
            UnpackerError: If the data could not be unpacked with the provided unpacker.

        """
        if not self._is_connected:
            await self.start()

        try:
            payload = await asyncio.get_running_loop().run_in_executor(self._executor, self._ser.readline, -1)
        except asyncio.CancelledError:
            await asyncio.shield(self._cancel_read())
            raise

        data, extra = self.unpacker(payload=payload)
        logger.debug(
            "SerialSource(%(port)s): Unpacked: %(data)s, extra information: %(extra)s",
            {"port": self.config.port, "data": data, "extra": extra},
        )
        return (data, extra)

    async def _cancel_read(self) -> None:
        if not hasattr(self, "_ser"):
            return
        logger.warning(
            "SerialSource(%(port)s).read() cancelled, waiting for %(timeout)s",
            {"port": self.config.port, "timeout": self._cancel_read_timeout},
        )
        await asyncio.wait_for(
            asyncio.get_running_loop().run_in_executor(self._executor, self._ser.cancel_read),
            self._cancel_read_timeout,
        )

    async def start(self) -> None:
        """Open serial device."""
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
        await self._cancel_read()
        self._ser.close()

    def __repr__(self) -> str:
        """Return string representation of Serial Source."""
        return f"SerialSource({self.config.port}, baudrate={self.config.baudrate})"
