from __future__ import annotations

import sys

import zmq
import zmq.asyncio

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import AsyncSource, Source

from .config import ZmqConf


class ZmqSubscriber(Source):
    """
    Source that subscribes to one or many topics from a zmq broker and receives messages via the receive() function.

    Attributes:
    -----------
    unpack : Callable
        The unpacker function to use for deserializing the data.

    Methods:
    --------
    receive() -> tuple[str, dict]:
        Send the data with the given topic.

    start():
        Connect to the socket.

    stop():
        Close the socket.
    """

    def __init__(self, config: ZmqConf, topic: str | list[str]):
        """
        Constructs new ZmqAsyncSubscriber instance.

        Parameters:
        -----------
        config : ZmqConf
            The configuration dataclass object for the zmq connection.
        topic : str
            The topic or list of topics to subscribe to.
        """
        self.config = config
        self.topic = topic
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.unpack = get_unpacker(config.packstyle)
        self.is_connected = False

    def receive(self) -> tuple[str, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: str, message: dict): the message received
        """
        if not self.is_connected:
            self.start()
        (topic, payload) = self.socket.recv_multipart()
        message = self.unpack(payload.decode())
        topic = topic.decode()
        return (topic, message)

    def start(self):
        try:
            self.socket.connect(self.config.subscriber_address)
            self.subscribe(self.topic)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)
        else:
            self.is_connected = True

    def stop(self):
        self.socket.close()
        self.is_connected = False

    def subscribe(self, topic: str | list[str] | tuple[str]):
        # Accepts single topic or list of topics
        if isinstance(topic, (list, tuple)):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    def _subscribe_single_topic(self, topic: str):
        self.socket.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.subscriber_address}, port={self.config.subscriber_port})"


class ZmqAsyncSubscriber(AsyncSource):
    """
    Async source that subscribes to one or many topics from a zmq broker and receives messages via the receive() function.

    Attributes:
    -----------
    unpack : Callable
        The unpacker function to use for deserializing the data.

    Methods:
    --------
    receive() -> tuple[str, dict]:
        Send the data with the given topic.

    start():
        Connect to the socket.

    stop():
        Close the socket.
    """

    def __init__(self, config: ZmqConf, topic: str | list[str]):
        """
        Constructs new ZmqAsyncSubscriber instance.

        Parameters:
        -----------
        config : ZmqConf
            The configuration dataclass object for the zmq connection.
        topic : str
            The topic or list of topics to subscribe to.
        """
        self.config = config
        self.topic = topic
        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.SUB)
        self.unpack = get_unpacker(config.packstyle)
        self.is_connected = False

    async def receive(self) -> tuple[str, dict]:
        """
        reads a message from the zmq bus and returns it

        Returns:
            tuple(topic: str, message: dict): the message received
        """
        if not self.is_connected:
            self.start()
        (topic, payload) = await self.socket.recv_multipart()
        message = self.unpack(payload.decode())
        topic = topic.decode()
        return (topic, message)

    def start(self):
        """Connect to the zmq socket."""
        try:
            self.socket.connect(self.config.subscriber_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)
        else:
            self.is_connected = True
        self.subscribe(self.topic)

    def stop(self):
        """Close the zmq socket."""
        self.socket.close()
        self.is_connected = False

    def subscribe(self, topic: str | list[str] | tuple[str]):
        """
        Subscribes to the given topic(s) on the zmq socket.

        Accepts single topic or list of topics.
        """
        if isinstance(topic, (list, tuple)):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    def _subscribe_single_topic(self, topic: str):
        self.socket.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.subscriber_address}, port={self.config.subscriber_port})"
