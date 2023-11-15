import socket

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Serializable, Sink
from heisskleber.udp.config import UdpConf


class UdpPublisher(Sink):
    def __init__(self, config: UdpConf) -> None:
        self.config = config
        self.ip = self.config.ip
        self.port = self.config.port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pack = get_packer(self.config.packer)

    def send(self, message: dict[str, Serializable], topic: str) -> None:
        message["topic"] = topic
        payload = self.pack(message).encode("utf-8")
        self.socket.sendto(payload, (self.ip, self.port))

    def __del__(self) -> None:
        self.socket.close()
