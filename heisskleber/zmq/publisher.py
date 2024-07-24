import sys
from typing import Any, Callable

import zmq
import zmq.asyncio

from heisskleber.core.packer import json_packer
from heisskleber.core.types import AsyncSink

from .config import ZmqConf


class ZmqAsyncPublisher(AsyncSink):
    """
    Async publisher that sends messages to a ZMQ PUB socket.

    Attributes:
    -----------
    pack : Callable
        The packer strategy to use for serializing the data.
        Defaults to json packer with utf-8 encoding.

    Methods:
    --------
    send(data : dict, topic : str):
        Send the data with the given topic.

    start():
        Connect to the socket.

    stop():
        Close the socket.
    """

    def __init__(self, config: ZmqConf, packer: Callable[[dict[str, Any]], bytes] = json_packer):
        self.config = config
        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.PUB)
        self.pack: Callable = packer
        self.is_connected = False

    async def send(self, data: dict[str, Any], topic: str) -> None:
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
