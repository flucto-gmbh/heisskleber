from dataclasses import dataclass

from heisskleber.config import BaseConf


@dataclass
class ZmqConf(BaseConf):
    protocol: str = "tcp"
    interface: str = "127.0.0.1"
    publisher_port: int = 5555
    subscriber_port: int = 5556
    packstyle: str = "json"

    @property
    def publisher_address(self) -> str:
        return f"{self.protocol}://{self.interface}:{self.publisher_port}"

    @property
    def subscriber_address(self) -> str:
        return f"{self.protocol}://{self.interface}:{self.subscriber_port}"
