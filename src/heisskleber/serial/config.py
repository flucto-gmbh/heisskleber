from dataclasses import dataclass

from heisskleber.core.config import BaseConf


@dataclass
class SerialConf(BaseConf):
    """Serial Config class.

    Attributes:
      port: The port to connect to. Defaults to /dev/serial0.
      baudrate: The baudrate of the serial connection. Defaults to 9600.
      bytesize: The bytesize of the messages. Defaults to 8.
      encoding: The string encoding of the messages. Defaults to ascii.

    """

    port: str = "/dev/serial0"
    baudrate: int = 9600
    bytesize: int = 8
    encoding: str = "ascii"
