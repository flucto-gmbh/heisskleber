import logging
from typing import Any, TypeVar

import zmq
import zmq.asyncio

from heisskleber.core import Receiver, Unpacker, json_unpacker
from heisskleber.zmq.config import ZmqConf

logger = logging.getLogger("heisskleber.zmq")


T = TypeVar("T")


class ZmqReceiver(Receiver[T]):
    """Async source that subscribes to one or many topics from a zmq broker and receives messages via the receive() function.

    Attributes:
        config: The ZmqConf configuration object for the connection.
        unpacker : The unpacker function to use for deserializing the data.


    """

    def __init__(self, config: ZmqConf, topic: str | list[str], unpacker: Unpacker[T] = json_unpacker) -> None:  # type: ignore [assignment]
        self.config = config
        self.topic = topic
        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.SUB)
        self.unpack = unpacker
        self.is_connected = False

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Read a message from the zmq bus and return it.

        Returns:
            tuple(topic: str, message: dict): the message received

        Raises:
            UnpackerError: If payload could not be unpacked with provided unpacker.

        """
        if not self.is_connected:
            await self.start()
        (topic, payload) = await self.socket.recv_multipart()
        data, extra = self.unpack(payload)
        extra["topic"] = topic.decode()
        return data, extra

    async def start(self) -> None:
        """Connect to the zmq socket."""
        try:
            self.socket.connect(self.config.subscriber_address)
        except Exception:
            logger.exception("Failed to bind to zeromq socket")
        else:
            self.is_connected = True
        self.subscribe(self.topic)

    async def stop(self) -> None:
        """Close the zmq socket."""
        self.socket.close()
        self.is_connected = False

    def subscribe(self, topic: str | list[str] | tuple[str]) -> None:
        """Subscribe to the given topic(s) on the zmq socket.

        Arguments:
        ---------
            topic: The topic or list of topics to subscribe to.

        """
        if isinstance(topic, (list, tuple)):
            for t in topic:
                self._subscribe_single_topic(t)
        else:
            self._subscribe_single_topic(topic)

    def _subscribe_single_topic(self, topic: str) -> None:
        self.socket.setsockopt(zmq.SUBSCRIBE, topic.encode())

    def __repr__(self) -> str:
        """Return string representation of ZmqSource."""
        return f"{self.__class__.__name__}(host={self.config.subscriber_address}, port={self.config.subscriber_port})"
