import socket
import sys

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Serializable, Sink
from heisskleber.udp.config import UdpConf


class UdpPublisher(Sink):
    def __init__(self, config: UdpConf) -> None:
        self.config = config
        self.ip = self.config.host
        self.port = self.config.port
        self.pack = get_packer(self.config.packer)
        self.is_connected = False

    def start(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except OSError as e:
            print(f"failed to create socket: {e}")
            sys.exit(-1)
        else:
            self.is_connected = True

    def stop(self) -> None:
        self.socket.close()
        self.is_connected = True

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        if not self.is_connected:
            self.start()
        data["topic"] = topic
        payload = self.pack(data).encode("utf-8")
        self.socket.sendto(payload, (self.ip, self.port))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
