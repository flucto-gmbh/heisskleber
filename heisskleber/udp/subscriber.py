import socket

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import Subscriber
from heisskleber.udp.config import UDPConf


class UDP_Subscriber(Subscriber):
    def __init__(self, config, topic=None):
        self.config = config
        self.ip = self.config.ip
        self.port = self.config.port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.unpacker = get_unpacker(self.config.packer)

    def receive(self):
        payload, addr = self.socket.recvfrom(1024)
        return addr, self.unpacker(payload.decode("utf-8"))

    def listen_loop(self):
        while True:
            addr, data = self.receive()
            print(type(data))
            print(data)

    def __del__(self):
        self.socket.close()


if __name__ == "__main__":
    conf = UDPConf(ip="192.168.1.122", port=12345)
    sub = UDP_Subscriber(conf)
    sub.listen_loop()
