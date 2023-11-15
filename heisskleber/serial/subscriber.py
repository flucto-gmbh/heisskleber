from __future__ import annotations

from collections.abc import Generator
from typing import Callable, Optional

import serial

from heisskleber.core.types import Source

from .config import SerialConf


class SerialSubscriber(Source):
    """
    Subscriber for serial devices. Connects to a serial port and reads from it.

    Parameters
    ----------
    topics :
        Placeholder for topic. Not used.

    config : SerialConf
        Configuration class for the serial connection.

    unpack_func : FunctionType
        Function to translate from a serialized string to a dict.
    """

    def __init__(
        self,
        config: SerialConf,
        topic: str | None = None,
        custom_unpack: Optional[Callable] = None,  # noqa: UP007
    ):
        self.config = config
        self.topic = topic
        self.unpack = custom_unpack if custom_unpack else lambda x: x  # types: ignore
        self._connect()

    def _connect(self):
        self.serial: serial.Serial = serial.Serial(
            port=self.config.port,
            baudrate=self.config.baudrate,
            bytesize=self.config.bytesize,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        print(f"Successfully connected to serial device at port {self.config.port}")

    def receive(self) -> tuple[str, dict]:
        """
        Wait for data to arrive on the serial port and return it.

        Returns
        -------
        :return: (topic, payload)
            topic is a placeholder to adhere to the Subscriber interface
            payload is a dictionary containing the data from the serial port
        """
        # message is a string
        message = next(self.read_serial_port())
        # payload is a dictionary
        payload = self.unpack(message)
        # port is a placeholder for topic
        return self.config.port, payload

    def read_serial_port(self) -> Generator[str, None, None]:
        """
        Generator function reading from the serial port.

        Returns
        -------
        :return: Generator[str, None, None]
            Generator yielding strings read from the serial port
        """
        buffer = ""
        while True:
            try:
                buffer = self.serial.readline().decode(self.config.encoding, "ignore")
                yield buffer
            except UnicodeError as e:
                if self.config.verbose:
                    print(f"Could not decode: {buffer!r}")
                    print(e)
                continue

    def __del__(self) -> None:
        if not hasattr(self, "serial"):
            return
        if not self.serial.is_open:
            return
        self.serial.flush()
        self.serial.close()
