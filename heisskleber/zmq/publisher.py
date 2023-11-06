import sys
from typing import Any

import zmq

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Publisher

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

    def send(self, topic: str, data: dict[str, Any]) -> None:
        payload = self.pack(data)
        self.socket.send_multipart([topic, payload.encode("utf-8")])

    def __del__(self):
        self.socket.close()
