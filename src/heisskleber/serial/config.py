from dataclasses import dataclass
from typing import Literal

from heisskleber.core.config import BaseConf


@dataclass
class SerialConf(BaseConf):
    """Serial Config class.

    Attributes:
      port: The port to connect to. Defaults to /dev/serial0.
      baudrate: The baudrate of the serial connection. Defaults to 9600.
      bytesize: The bytesize of the messages. Defaults to 8.
      encoding: The string encoding of the messages. Defaults to ascii.
      parity: The parity checking value. One of "N" for none, "E" for even, "O" for odd. Defaults to None.
      stopbits: Stopbits. One of 1, 2 or 1.5. Defaults to 1.

    Note:
      stopbits 1.5 is not yet implemented.

    """

    port: str = "/dev/serial0"
    baudrate: int = 9600
    bytesize: int = 8
    encoding: str = "ascii"
    parity: Literal["N", "O", "E"] = "N"  # definitions from serial.PARTITY_'N'ONE / 'O'DD / 'E'VEN
    stopbits: Literal[1, 2] = 1  # 1.5 not yet implemented
