import logging
from asyncio import Queue, Task, create_task, sleep
from typing import Any, TypeVar

import aiomqtt

from heisskleber.core import AsyncSink, Packer, json_packer

from .config import MqttConf

T = TypeVar("T")

log = logging.getLogger(__name__)


class AsyncMqttPublisher(AsyncSink[T]):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MqttConf, packer: Packer[T] = json_packer) -> None:
        self.config = config
        self.pack = packer
        self._send_queue: Queue[tuple[T, str]] = Queue()
        self._sender_task: Task[None] | None = None

    async def send(
        self, data: T, topic: str = "mqtt", qos: int = 0, retain: bool = False, **kwargs: dict[str, Any]
    ) -> None:
        """
        Takes python dictionary, serializes it with the packer of the AsyncSink class
        and sends it to the broker.

        Publishing is asynchronous
        """
        if not self._sender_task:
            await self.start()

        await self._send_queue.put((data, topic))

    async def send_work(self) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
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
                        payload = self.pack(data)
                        await client.publish(topic=topic, payload=payload)
            except aiomqtt.MqttError:
                print("Connection to MQTT broker failed. Retrying in 5 seconds")
                await sleep(5)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    async def start(self) -> None:
        self._sender_task = create_task(self.send_work())

    def stop(self) -> None:
        if self._sender_task:
            self._sender_task.cancel()
            self._sender_task = None
