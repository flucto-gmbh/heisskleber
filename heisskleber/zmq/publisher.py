import sys

import zmq
import zmq.asyncio

from heisskleber.core.packer import get_packer
from heisskleber.core.types import AsyncSink, Serializable, Sink

from .config import ZmqConf


class ZmqPublisher(Sink):
    def __init__(self, config: ZmqConf):
        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        self.pack = get_packer(config.packstyle)
        self.connect()

    def connect(self) -> None:
        try:
            if self.config.verbose:
                print(f"connecting to {self.config.publisher_address}")
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        payload = self.pack(data)
        if self.config.verbose:
            print(f"sending message {payload} to topic {topic}")
        self.socket.send_multipart([topic.encode(), payload.encode()])

    def __del__(self):
        self.socket.close()


class ZmqAsyncPublisher(AsyncSink):
    def __init__(self, config: ZmqConf):
        self.config = config

        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.PUB)

        self.pack = get_packer(config.packstyle)
        self.connect()

    def connect(self) -> None:
        try:
            if self.config.verbose:
                print(f"connecting to {self.config.publisher_address}")
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    async def send(self, data: dict[str, Serializable], topic: str) -> None:
        payload = self.pack(data)
        if self.config.verbose:
            print(f"sending message {payload} to topic {topic}")
        await self.socket.send_multipart([topic.encode(), payload.encode()])

    def __del__(self):
        self.socket.close()
