from __future__ import annotations

import sys
from typing import Callable, Optional

import serial

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Serializable, Sink

from .config import SerialConf


class SerialPublisher(Sink):
    serial_connection: serial.Serial
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
        self.is_connected = False

    def start(self) -> None:
        """
        Start the serial connection.
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
        except serial.SerialException:
            print(f"Failed to connect to serial device at port {self.config.port}")
            sys.exit(1)

        print(f"Successfully connected to serial device at port {self.config.port}")
        self.is_connected = True

    def stop(self) -> None:
        """
        Stop the serial connection.
        """
        if hasattr(self, "serial_connection") and self.serial_connection.is_open:
            self.serial_connection.flush()
            self.serial_connection.close()

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Parameters
        ----------
        message : dict
            object to be serialized and sent via the serial connection. Usually a dict.
        """
        if not self.is_connected:
            self.start()

        payload = self.pack(data)
        self.serial_connection.write(payload.encode(self.config.encoding))
        self.serial_connection.flush()
        if self.config.verbose:
            print(f"{topic}: {payload}")

    def __repr__(self) -> str:
        return f"SerialPublisher(port={self.config.port}, baudrate={self.config.baudrate}, bytezize={self.config.bytesize}, encoding={self.config.encoding})"

    def __del__(self) -> None:
        self.stop()
