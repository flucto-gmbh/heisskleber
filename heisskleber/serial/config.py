from dataclasses import dataclass

from heisskleber.config import BaseConf


@dataclass
class SerialConf(BaseConf):
    port: str = "/dev/serial0"
    baudrate: int = 9600
    bytesize: int = 8
    encoding: str = "ascii"
