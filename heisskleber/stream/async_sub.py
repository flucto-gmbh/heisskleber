from asyncio import Queue

from aiomqtt import Client, Message

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import AsyncSubscriber, Serializable
from heisskleber.mqtt import MqttConf


class AsyncMQTTSubscriber(AsyncSubscriber):
    def __init__(self, config: MqttConf, topic: str | list[str]) -> None:
        self.config: MqttConf = config
        self.client = Client(
            hostname=self.config.broker,
            port=self.config.port,
            username=self.config.user,
            password=self.config.password,
        )
        self.topics = topic
        self.unpack = get_unpacker(self.config.packstyle)
        self.message_queue: Queue[Message] = Queue(self.config.max_saved_messages)

    async def __anext__(
        self,
    ) -> tuple[str, dict[str, Serializable]] | None:  # Do I really need to return None?
        # Context manager that buffers mqtt messages
        try:
            return await self.receive()
        except Exception:
            raise StopAsyncIteration  # noqa: B904

    def __aiter__(self) -> AsyncSubscriber:
        return self

    async def _subscribe_topics(self) -> None:
        print(f"subscribing to {self.topics}")
        if isinstance(self.topics, list):
            await self.client.subscribe(
                [(topic, self.config.qos) for topic in self.topics]
            )
        else:
            await self.client.subscribe(self.topics, self.config.qos)

    """
    Await the newest message in the queue and return Tuple
    """

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        mqtt_message: Message = await self.message_queue.get()
        topic = str(mqtt_message.topic)
        if not isinstance(mqtt_message.payload, bytes):
            error_msg = "Payload is not of type bytes."
            raise TypeError(error_msg)
        message_returned = self.unpack(mqtt_message.payload.decode())
        return (topic, message_returned)

    """
    Listen to incoming messages asynchronously and put them into a queue
    """

    async def start_loop(self) -> None:
        # Manage connection to mqtt
        async with self.client:
            await self._subscribe_topics()
            await self._listen_mqtt_loop()

    async def _listen_mqtt_loop(self) -> None:
        async with self.client.messages() as messages:
            # async with self.client.filtered_messages(self.topics) as messages:
            async for message in messages:
                await self.message_queue.put(message)
