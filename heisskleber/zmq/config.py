from dataclasses import dataclass

from heisskleber.core import BaseConf


@dataclass
class ZmqConf(BaseConf):
    """ZMQ Configuration file."""

    protocol: str = "tcp"
    host: str = "127.0.0.1"
    publisher_port: int = 5555
    subscriber_port: int = 5556
    packstyle: str = "json"

    @property
    def publisher_address(self) -> str:
        """Return the full url to connect to the publisher port."""
        return f"{self.protocol}://{self.host}:{self.publisher_port}"

    @property
    def subscriber_address(self) -> str:
        """Return the full url to connect to the subscriber port."""
        return f"{self.protocol}://{self.host}:{self.subscriber_port}"
