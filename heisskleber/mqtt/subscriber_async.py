from asyncio import Queue, Task, create_task, sleep

from aiomqtt import Client, Message, MqttError

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import AsyncSource, Serializable
from heisskleber.mqtt import MqttConf


class AsyncMqttSubscriber(AsyncSource):
    """Asynchronous MQTT susbsciber based on aiomqtt.

    Data is received by the `receive` method returns the newest message in the queue.
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
        self._listener_task: Task = create_task(self.create_listener())

    """
    Await the newest message in the queue and return Tuple
    """

    def __del__(self):
        self._listener_task.cancel()

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        mqtt_message: Message = await self.message_queue.get()
        return self._handle_message(mqtt_message)

    async def create_listener(self):
        while True:
            try:
                async with self.client:
                    await self._subscribe_topics()
                    await self._listen_mqtt_loop()
            except MqttError as e:
                print(f"MqttError: {e}")
                print("Connection to MQTT failed. Retrying...")
                await sleep(1)

    """
    Listen to incoming messages asynchronously and put them into a queue
    """

    async def _listen_mqtt_loop(self) -> None:
        async with self.client.messages() as messages:
            # async with self.client.filtered_messages(self.topics) as messages:
            async for message in messages:
                await self.message_queue.put(message)

    def _handle_message(self, message: Message) -> tuple[str, dict[str, Serializable]]:
        if not isinstance(message.payload, bytes):
            error_msg = "Payload is not of type bytes."
            raise TypeError(error_msg)

        topic = str(message.topic)
        message_returned = self.unpack(message.payload.decode())
        return (topic, message_returned)

    async def _subscribe_topics(self) -> None:
        print(f"subscribing to {self.topics}")
        if isinstance(self.topics, list):
            await self.client.subscribe([(topic, self.config.qos) for topic in self.topics])
        else:
            await self.client.subscribe(self.topics, self.config.qos)
