from dataclasses import dataclass

from heisskleber.config import BaseConf


@dataclass
class UdpConf(BaseConf):
    """
    UDP configuration.
    """

    port: int = 1234
    host: str = "127.0.0.1"
    packer: str = "json"
    max_queue_size: int = 1000
    encoding: str = "utf-8"
    delimiter: str = "\r\n"
