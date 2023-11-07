from dataclasses import dataclass

from heisskleber.config import BaseConf


@dataclass
class UdpConf(BaseConf):
    """
    UDP configuration.
    """

    port: int = 1234
    ip: str = "127.0.0.1"
    packer: str = "json"
