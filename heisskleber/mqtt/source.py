from asyncio import Queue, Task, create_task, sleep
from typing import Any, TypeVar

from aiomqtt import Client, Message, MqttError

from heisskleber.core import AsyncSource, Unpacker, json_unpacker
from heisskleber.mqtt import MqttConf

T = TypeVar("T")


class MqttSource(AsyncSource[T]):
    """Asynchronous MQTT susbsciber based on aiomqtt.

    Data is received by the `receive` method returns the newest message in the queue.
    """

    def __init__(self, config: MqttConf, topic: str | list[str], unpacker: Unpacker[T] = json_unpacker) -> None:
        self.config = config
        # TODO: Move to start method
        self.client = Client(
            hostname=self.config.host,
            port=self.config.port,
            username=self.config.user,
            password=self.config.password,
        )
        self.topics = topic
        self.unpack = unpacker
        self.message_queue: Queue[Message] = Queue(self.config.max_saved_messages)
        self._listener_task: Task[None] | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    async def start(self) -> None:
        self._listener_task = create_task(self._run())

    def stop(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
        self._listener_task = None

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """
        Await the newest message in the queue and return Tuple
        """
        if not self._listener_task:
            await self.start()

        message = await self.message_queue.get()
        if not isinstance(message.payload, bytes):
            error_msg = "Payload is not of type bytes."
            raise TypeError(error_msg)

        data, extra = self.unpack(message.payload)
        extra["topic"] = message.topic
        return (data, extra)

    async def subscribe(self, topic: str, qos: int | None = None) -> None:
        qos = qos or self.config.qos
        await self.client.subscribe(topic, qos)

    async def _run(self):
        """
        Handle the connection to MQTT broker and run the message loop.
        """
        while True:
            try:
                async with self.client:
                    await self._subscribe_topics()
                    await self._listen_mqtt_loop()
            except MqttError as e:
                print(f"MqttError: {e}")
                print("Connection to MQTT failed. Retrying...")
                await sleep(1)

    async def _listen_mqtt_loop(self) -> None:
        """
        Listen to incoming messages asynchronously and put them into a queue
        """
        async with self.client.messages() as messages:
            async for message in messages:
                await self.message_queue.put(message)

    async def _subscribe_topics(self) -> None:
        print(f"subscribing to {self.topics}")
        if isinstance(self.topics, list):
            await self.client.subscribe([(topic, self.config.qos) for topic in self.topics])
        else:
            await self.client.subscribe(self.topics, self.config.qos)
