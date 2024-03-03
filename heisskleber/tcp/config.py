from dataclasses import dataclass

from heisskleber.config import BaseConf


@dataclass
class TcpConf(BaseConf):
    host: str = "localhost"
    port: int = 6000
    timeout: int = 60
