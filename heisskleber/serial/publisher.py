from __future__ import annotations

from typing import Callable, Optional

import serial

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Serializable, Sink

from .config import SerialConf


class SerialPublisher(Sink):
    """
    Publisher for serial devices.
    Can be used everywhere that a flucto style publishing connection is required.

    Parameters
    ----------
    config : SerialConf
        Configuration for the serial connection.
    pack_func : FunctionType
        Function to translate from a dict to a serialized string.
    """

    def __init__(
        self,
        config: SerialConf,
        pack_func: Optional[Callable] = None,  # noqa: UP007
    ):
        self.config = config
        self.pack = pack_func if pack_func else get_packer("serial")
        self._connect()

    def _connect(self) -> None:
        self.serial: serial.Serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.bytesize,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        print(f"Successfully connected to serial device at port {self.config.port}")

    def send(self, message: dict[str, Serializable], topic: str) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Parameters
        ----------
        message : dict
            object to be serialized and sent via the serial connection. Usually a dict.
        """
        payload = self.pack(message)
        self.serial.write(payload.encode(self.config.encoding))
        self.serial.flush()
        if self.config.verbose:
            print(f"{topic}: {payload}")

    def __del__(self) -> None:
        if not hasattr(self, "serial"):
            return
        if not self.serial.is_open:
            return
        self.serial.flush()
        self.serial.close()
