from dataclasses import dataclass

from heisskleber.core import BaseConf


@dataclass
class SerialConf(BaseConf):
    """
    Serial Config class.

    Members:
      port (str): The port to connect to.
    """

    port: str = "/dev/serial0"
    baudrate: int = 9600
    bytesize: int = 8
    encoding: str = "ascii"
