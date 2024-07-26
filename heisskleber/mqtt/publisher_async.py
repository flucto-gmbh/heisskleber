import logging
from asyncio import Queue, Task, create_task, sleep
from typing import Any, Generic, Optional, TypedDict, TypeVar, Type

import aiomqtt
from typing_extensions import NotRequired

from heisskleber.core import AsyncSink, Packer, json_packer

from .config import MqttConf

T = TypeVar("T")

log = logging.getLogger(__name__)


class MqttExtra(TypedDict):
    topic: str
    qos: NotRequired[int]
    retain: NotRequired[bool]


class AsyncMqttPublisher(AsyncSink[T, MqttExtra]):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MqttConf, packer: Packer[T] = json_packer) -> None:
        self.config = config
        self.pack = packer
        self._send_queue: Queue[tuple[T, MqttExtra]] = Queue()
        self._sender_task: Task[None] | None = None

    @classmethod
    def create(
        cls: type["AsyncMqttPublisher[T]"], config: MqttConf, packer: Packer[T] = json_packer
    ) -> "AsyncMqttPublisher[T]":
        return cls(config, packer)

    async def send(self, data: T, extra: MqttExtra | None = None) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        if not extra:
            log.warning("Can't send mqtt messages without topic!")
            raise TypeError

        if not self._sender_task:
            self.start()

        await self._send_queue.put((data, extra))

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
                        data, extra = await self._send_queue.get()
                        payload = self.pack(data)
                        await client.publish(topic=extra["topic"], payload=payload)
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


class FloatPacker(Packer[float]):
    def __call__(self, data: float) -> bytes:
        string_rep = f"{data}"
        return string_rep.encode()


async def main():
    config = MqttConf()
    packer = FloatPacker()
    pub = AsyncMqttPublisher(config, packer)
    normal_pub = AsyncMqttPublisher(config, json_packer)

    await pub.send(1.0, extra={"topic": "/test"})
    await normal_pub.send({"epoch": 1.0}, extra={"topic": "/test"})
