from __future__ import annotations

import sys

import zmq

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import Subscriber

from .config import ZmqConf


class ZmqSubscriber(Subscriber):
    def __init__(self, config: ZmqConf, topic: str):
        self.config = config

        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.connect()
        self.subscribe(topic)

        self.unpack = get_unpacker(config.packstyle)

    def connect(self):
        try:
            # print(f"Connecting to { self.config.consumer_connection }")
            self.socket.connect(self.config.subscriber_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def _subscribe_single_topic(self, topic: bytes | str):
        if isinstance(topic, str):
            topic = topic.encode()
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def subscribe(self, topic: bytes | str | list[bytes] | list[str]):
        # Accepts single topic or list of topics
        if isinstance(topic, (list, tuple)):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    def receive(self) -> tuple[bytes, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: bytes, message: dict): the message received
        """
        (topic, message) = self.socket.recv_multipart()
        message = self.unpack(message.decode())
        return (topic, message)

    def __del__(self):
        self.socket.close()
