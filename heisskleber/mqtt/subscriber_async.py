from asyncio import Queue, sleep

from aiomqtt import Client, Message, MqttError

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import AsyncSubscriber, Serializable
from heisskleber.mqtt import MqttConf


class AsyncMqttSubscriber(AsyncSubscriber):
    """Asynchronous MQTT susbsciber based on aiomqtt.

    Data is received by one of two methods:
    1. The `receive` method returns the newest message in the queue. For this to work, the `run` method must be called in a separae task.
    2. The `generator` method is a generator function that yields a topic and dict payload.
    """

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

    """
    Await the newest message in the queue and return Tuple
    """

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        mqtt_message: Message = await self.message_queue.get()
        return self._handle_message(mqtt_message)

    """
    Listen to incoming messages asynchronously and put them into a queue
    """

    async def run(self) -> None:
        """
        Run the async mqtt listening loop.
        Includes reconnecting to mqtt broker.
        """
        # Manage connection to mqtt
        while True:
            try:
                async with self.client:
                    await self._subscribe_topics()
                    await self._listen_mqtt_loop()
            except MqttError:
                print("Connection to MQTT failed. Retrying...")
                await sleep(1)

    """
    Generator function that yields topic and dict payload.
    """

    async def generator(self):
        while True:
            try:
                async with self.client:
                    await self._subscribe_topics()
                    async with self.client.messages() as messages:
                        async for message in messages:
                            yield self._handle_message(message)
            except MqttError:
                print("Connection to MQTT failed. Retrying...")
                await sleep(1)

    async def _listen_mqtt_loop(self) -> None:
        async with self.client.messages() as messages:
            # async with self.client.filtered_messages(self.topics) as messages:
            async for message in messages:
                await self.message_queue.put(message)

    def _handle_message(self, message: Message) -> tuple[str, dict[str, Serializable]]:
        topic = str(message.topic)
        if not isinstance(message.payload, bytes):
            error_msg = "Payload is not of type bytes."
            raise TypeError(error_msg)
        message_returned = self.unpack(message.payload.decode())
        return (topic, message_returned)

    async def _subscribe_topics(self) -> None:
        print(f"subscribing to {self.topics}")
        if isinstance(self.topics, list):
            await self.client.subscribe([(topic, self.config.qos) for topic in self.topics])
        else:
            await self.client.subscribe(self.topics, self.config.qos)
