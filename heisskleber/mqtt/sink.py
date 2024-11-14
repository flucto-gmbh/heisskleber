"""Async mqtt sink implementation."""

import logging
from asyncio import Queue, Task, create_task, sleep
from typing import Any, TypeVar

import aiomqtt

from heisskleber.core import AsyncSink, Packer, json_packer

from .config import MqttConf

T = TypeVar("T")

logger = logging.getLogger(__name__)


class MqttSink(AsyncSink[T]):
    """MQTT publisher with queued message handling.

    This sink implementation provides asynchronous MQTT publishing capabilities with automatic connection management and message queueing.
    Network operations are handled in a separate task.

    Attributes
    ----------
        config: MQTT configuration in a dataclass.
        packer: Callable to pack data from type T to bytes for transport.

    """

    def __init__(self, config: MqttConf, packer: Packer[T] = json_packer) -> None:  # type: ignore[assignment]
        self.config = config
        self.packer = packer
        self._send_queue: Queue[tuple[T, str]] = Queue()
        self._sender_task: Task[None] | None = None

    async def send(self, data: T, topic: str = "mqtt", qos: int = 0, retain: bool = False, **kwargs: Any) -> None:
        """Queue data for asynchronous publication to the mqtt broker.

        Arguments:
        ---------
            data: The data to be published.
            topic: The mqtt topic to publish to.
            qos: MQTT QOS level (0, 1, or 2). Defaults to 0.o
            retain: Whether to set the MQTT retain flag. Defaults to False.
            **kwargs: Not implemented.

        """
        if not self._sender_task:
            await self.start()

        await self._send_queue.put((data, topic))

    async def _send_work(self) -> None:
        # TODO: Clean shutdown
        # TODO: backoff style retry
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=self.config.host,
                    port=self.config.port,
                    username=self.config.user,
                    password=self.config.password,
                    timeout=float(self.config.timeout_s),
                ) as client:
                    while True:
                        data, topic = await self._send_queue.get()
                        payload = self.packer(data)
                        await client.publish(topic=topic, payload=payload)
            except aiomqtt.MqttError:
                logger.exception("Connection to MQTT broker failed. Retrying in 5 seconds")
                await sleep(5)

    def __repr__(self) -> str:
        """Return string representation of the MQTT sink object."""
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    async def start(self) -> None:
        """Start the send queue in a separate task.

        The task will retry connections every 5 seconds on failure.
        """
        self._sender_task = create_task(self._send_work())

    def stop(self) -> None:
        """Stop the background task."""
        if self._sender_task:
            self._sender_task.cancel()
            self._sender_task = None
