import sys
from typing import Callable

import zmq
import zmq.asyncio

from heisskleber.core.packer import get_packer
from heisskleber.core.types import AsyncSink, Serializable, Sink

from .config import ZmqConf


class ZmqPublisher(Sink):
    """
    Publisher that sends messages to a ZMQ PUB socket.

    Attributes:
    -----------
    pack : Callable
        The packer function to use for serializing the data.

    Methods:
    --------
    send(data : dict, topic : str):
        Send the data with the given topic.

    start():
        Connect to the socket.

    stop():
        Close the socket.
    """

    def __init__(self, config: ZmqConf):
        self.config = config
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)
        self.pack = get_packer(config.packstyle)
        self.is_connected = False

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        """
        Take the data as a dict, serialize it with the given packer and send it to the zmq socket.
        """
        if not self.is_connected:
            self.start()
        payload = self.pack(data)
        if self.config.verbose:
            print(f"sending message {payload} to topic {topic}")
        self.socket.send_multipart([topic.encode(), payload.encode()])

    def start(self) -> None:
        """Connect to the zmq socket."""
        try:
            if self.config.verbose:
                print(f"connecting to {self.config.publisher_address}")
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)
        else:
            self.is_connected = True

    def stop(self) -> None:
        self.socket.close()
        self.is_connected = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.publisher_address}, port={self.config.publisher_port})"


class ZmqAsyncPublisher(AsyncSink):
    """
    Async publisher that sends messages to a ZMQ PUB socket.

    Attributes:
    -----------
    pack : Callable
        The packer function to use for serializing the data.

    Methods:
    --------
    send(data : dict, topic : str):
        Send the data with the given topic.

    start():
        Connect to the socket.

    stop():
        Close the socket.
    """

    def __init__(self, config: ZmqConf):
        self.config = config
        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.PUB)
        self.pack: Callable = get_packer(config.packstyle)
        self.is_connected = False

    async def send(self, data: dict[str, Serializable], topic: str) -> None:
        """
        Take the data as a dict, serialize it with the given packer and send it to the zmq socket.
        """
        if not self.is_connected:
            self.start()
        payload = self.pack(data)
        if self.config.verbose:
            print(f"sending message {payload} to topic {topic}")
        await self.socket.send_multipart([topic.encode(), payload.encode()])

    def start(self) -> None:
        """Connect to the zmq socket."""
        try:
            if self.config.verbose:
                print(f"connecting to {self.config.publisher_address}")
            self.socket.connect(self.config.publisher_address)
        except Exception as e:
            print(f"failed to bind to zeromq socket: {e}")
            sys.exit(-1)
        else:
            self.is_connected = True

    def stop(self) -> None:
        """Close the zmq socket."""
        self.socket.close()
        self.is_connected = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.publisher_address}, port={self.config.publisher_port})"
