import sys
from collections.abc import Generator
from typing import Callable

import serial

from heisskleber.core.types import Source

from .config import SerialConf


class SerialSubscriber(Source):
    serial_connection: serial.Serial
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
        custom_unpack: Callable | None = None,
    ):
        self.config = config
        self.topic = topic
        self.unpack = custom_unpack if custom_unpack else lambda x: x  # types: ignore
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

    def receive(self) -> tuple[str, dict]:
        """
        Wait for data to arrive on the serial port and return it.

        Returns
        -------
        :return: (topic, payload)
            topic is a placeholder to adhere to the Subscriber interface
            payload is a dictionary containing the data from the serial port
        """
        if not self.is_connected:
            self.start()

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
                buffer = self.serial_connection.readline().decode(self.config.encoding, "ignore")
                yield buffer
            except UnicodeError as e:
                if self.config.verbose:
                    print(f"Could not decode: {buffer!r}")
                    print(e)
                continue

    def __repr__(self) -> str:
        return f"SerialPublisher(port={self.config.port}, baudrate={self.config.baudrate}, bytezize={self.config.bytesize}, encoding={self.config.encoding})"

    def __del__(self) -> None:
        self.stop()
