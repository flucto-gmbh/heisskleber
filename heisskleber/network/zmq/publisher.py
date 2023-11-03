import sys

import zmq

from heisskleber.network.packer import get_packer
from heisskleber.network.pubsub.types import Publisher

from .config import ZmqConf


class ZmqPublisher(Publisher):
    def __init__(self, config: ZmqConf):
        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.pack = get_packer(config.packstyle)
        self.connect()

    def connect(self) -> None:
        try:
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def send(self, topic: str, data: dict) -> None:
        data = self.pack(data)
        self.socket.send_multipart([topic, data.encode("utf-8")])

    def __del__(self):
        self.socket.close()
