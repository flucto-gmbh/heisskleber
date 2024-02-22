from __future__ import annotations

import sys

import zmq
import zmq.asyncio

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import AsyncSource, Source

from .config import ZmqConf


class ZmqSubscriber(Source):
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

    def _subscribe_single_topic(self, topic: str):
        self.socket.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def subscribe(self, topic: str | list[str] | tuple[str]):
        # Accepts single topic or list of topics
        if isinstance(topic, (list, tuple)):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    def receive(self) -> tuple[str, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: str, message: dict): the message received
        """
        (topic, payload) = self.socket.recv_multipart()
        message = self.unpack(payload.decode())
        topic = topic.decode()
        return (topic, message)

    def __del__(self):
        self.socket.close()


class ZmqAsyncSubscriber(AsyncSource):
    def __init__(self, config: ZmqConf, topic: str):
        self.config = config
        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.SUB)
        self.connect()
        self.subscribe(topic)

        self.unpack = get_unpacker(config.packstyle)

    def connect(self):
        try:
            self.socket.connect(self.config.subscriber_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)

    def _subscribe_single_topic(self, topic: str):
        self.socket.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def subscribe(self, topic: str | list[str] | tuple[str]):
        # Accepts single topic or list of topics
        if isinstance(topic, (list, tuple)):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    async def receive(self) -> tuple[str, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: str, message: dict): the message received
        """
        (topic, payload) = await self.socket.recv_multipart()
        message = self.unpack(payload.decode())
        topic = topic.decode()
        return (topic, message)

    def __del__(self):
        self.socket.close()
