from asyncio import Queue, Task, create_task, sleep
from typing import Any, TypeVar
import logging

from aiomqtt import Client, Message, MqttError

from heisskleber.core import AsyncSource, Unpacker, json_unpacker
from heisskleber.mqtt import MqttConf

T = TypeVar("T")
logger = logging.getLogger("heisskleber.mqtt")


class MqttSource(AsyncSource[T]):
    """Asynchronous MQTT subscriber based on aiomqtt.

    This class implements an asynchronous MQTT subscriber that handles connection, subscription, and message reception from an MQTT broker. It uses aiomqtt as the underlying MQTT client implementation.

    The subscriber maintains a queue of received messages which can be accessed through the `receive` method.

    Attributes:
        config (MqttConf): Stored configuration for MQTT connection.
        topics (Union[str, List[str]]): Topics to subscribe to.
    """

    def __init__(self, config: MqttConf, topic: str | list[str], unpacker: Unpacker[T] = json_unpacker) -> None:
        """Initialize the MQTT source.

        Args:
            config: Configuration object containing:
                - host (str): MQTT broker hostname
                - port (int): MQTT broker port
                - user (str): Username for authentication
                - password (str): Password for authentication
                - qos (int): Default Quality of Service level
                - max_saved_messages (int): Maximum queue size
            topic: Single topic string or list of topics to subscribe to
            unpacker: Function to deserialize received messages, defaults to json_unpacker
        """
        self.config = config
        # TODO: Move to start method
        self._client = Client(
            hostname=self.config.host,
            port=self.config.port,
            username=self.config.user,
            password=self.config.password,
        )
        self.topics = topic
        self.unpacker = unpacker
        self._message_queue: Queue[Message] = Queue(self.config.max_saved_messages)
        self._listener_task: Task[None] | None = None

    def __repr__(self) -> str:
        """String representation of Mqtt Source class."""
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    async def start(self) -> None:
        """Start the MQTT listener task."""
        self._listener_task = create_task(self._run())

    def stop(self) -> None:
        """Stop the MQTT listener task."""
        if self._listener_task:
            self._listener_task.cancel()
        self._listener_task = None

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Receive and process the next message from the queue.

        Returns:
            tuple[T, dict[str, Any]]
                - The unpacked message data
                - A dictionary with metadata including the message topic

        Raises:
            TypeError: If the message payload is not of type bytes.
            UnpackError: If the message could not be unpacked with the unpacker protocol.
        """
        if not self._listener_task:
            await self.start()

        message = await self._message_queue.get()
        if not isinstance(message.payload, bytes):
            error_msg = "Payload is not of type bytes."
            raise TypeError(error_msg)

        data, extra = self.unpacker(message.payload)
        extra["topic"] = message.topic
        return (data, extra)

    async def subscribe(self, topic: str, qos: int | None = None) -> None:
        """Subscribe to an additional MQTT topic.

        Args:
            topic: The topic to subscribe to
            qos: Quality of Service level, uses config.qos if None
        """
        qos = qos or self.config.qos
        await self._client.subscribe(topic, qos)

    async def _run(self) -> None:
        # TODO: Implement backoff re-connection strategy
        while True:
            try:
                async with self._client:
                    await self._subscribe_topics()
                    await self._listen_mqtt_loop()
            except MqttError:
                logger.exception("Connection to MQTT failed. Retrying...")
                await sleep(1)

    async def _listen_mqtt_loop(self) -> None:
        """Listen to incoming messages asynchronously and put them into a queue."""
        async with self._client.messages() as messages:
            async for message in messages:
                await self._message_queue.put(message)

    async def _subscribe_topics(self) -> None:
        """Subscribe to one or multiple topics."""
        logger.info("subscribing to %(topics)s", {"topics": self.topics})
        if isinstance(self.topics, list):
            await self._client.subscribe([(topic, self.config.qos) for topic in self.topics])
        else:
            await self._client.subscribe(self.topics, self.config.qos)
