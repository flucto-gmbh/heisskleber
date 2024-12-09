import logging
from typing import Any, TypeVar

import zmq
import zmq.asyncio

from heisskleber.core import Packer, Sender, json_packer

from .config import ZmqConf

logger = logging.getLogger("heisskleber.zmq")

T = TypeVar("T")


class ZmqSender(Sender[T]):
    """Async publisher that sends messages to a ZMQ PUB socket.

    Attributes:
        config: The ZmqConf configuration object for the connection.
        packer : The packer strategy to use for serializing the data.
            Defaults to json packer with utf-8 encoding.

    """

    def __init__(self, config: ZmqConf, packer: Packer[T] = json_packer) -> None:  # type: ignore[assignment]
        self.config = config
        self.context = zmq.asyncio.Context.instance()
        self.socket: zmq.asyncio.Socket = self.context.socket(zmq.PUB)
        self.packer = packer
        self.is_connected = False

    async def send(self, data: T, topic: str = "zmq", **kwargs: Any) -> None:
        """Take the data as a dict, serialize it with the given packer and send it to the zmq socket."""
        if not self.is_connected:
            await self.start()
        payload = self.packer(data)
        logger.debug("sending payload %(payload)b to topic %(topic)s", {"payload": payload, "topic": topic})
        await self.socket.send_multipart([topic.encode(), payload])

    async def start(self) -> None:
        """Connect to the zmq socket."""
        logger.info("Connecting to %(addr)s", {"addr": self.config.publisher_address})
        self.socket.connect(self.config.publisher_address)
        self.is_connected = True

    async def stop(self) -> None:
        """Close the zmq socket."""
        self.socket.close()
        self.is_connected = False

    def __repr__(self) -> str:
        """Return string representation of ZmqSink."""
        return f"{self.__class__.__name__}(host={self.config.publisher_address}, port={self.config.publisher_port})"
