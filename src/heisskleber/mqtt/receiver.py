import asyncio
import logging
import ssl
from asyncio import Queue, Task, create_task
from typing import Any, TypeVar

import aiomqtt
from aiomqtt import Client, Message, MqttError

from heisskleber.core import Receiver, Unpacker, json_unpacker
from heisskleber.core.utils import retry
from heisskleber.mqtt import MqttConf

T = TypeVar("T")
logger = logging.getLogger("heisskleber.mqtt")


class MqttReceiver(Receiver[T]):
    """Asynchronous MQTT subscriber based on aiomqtt.

    This class implements an asynchronous MQTT subscriber that handles connection, subscription, and message reception from an MQTT broker. It uses aiomqtt as the underlying MQTT client implementation.

    The subscriber maintains a queue of received messages which can be accessed through the `receive` method.

    Attributes:
        config (MqttConf): Stored configuration for MQTT connection.
        topics (Union[str, List[str]]): Topics to subscribe to.

    """

    def __init__(
        self,
        config: MqttConf,
        topic: str | list[str],
        unpacker: Unpacker[T] = json_unpacker,  # type: ignore[assignment]
    ) -> None:
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
        self.topics = topic if isinstance(topic, list) else [topic]
        self.unpacker = unpacker
        self._message_queue: Queue[Message] = Queue(self.config.max_saved_messages)
        self._listener_task: Task[None] | None = None

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Receive and process the next message from the queue.

        Returns:
            tuple[T, dict[str, Any]]
                - The unpacked message data
                - A dictionary with metadata including the message topic

        Raises:
            TypeError: If the message payload is not of type bytes.
            UnpackerError: If the message could not be unpacked with the unpacker protocol.

        """
        if not self._listener_task:
            await self.start()

        message = await self._message_queue.get()
        if not isinstance(message.payload, bytes):
            error_msg = "Payload is not of type bytes."
            raise TypeError(error_msg)

        data, extra = self.unpacker(message.payload)
        extra["topic"] = message.topic.value
        return (data, extra)

    def __repr__(self) -> str:
        """Return string representation of Mqtt Source class."""
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    async def start(self) -> None:
        """Start the MQTT listener task."""
        self._listener_task = create_task(self._run())

    async def stop(self) -> None:
        """Stop the MQTT listener task."""
        if not self._listener_task:
            return

        self._listener_task.cancel()
        try:
            await self._listener_task
        except asyncio.CancelledError:
            # Raise if the stop task was cancelled
            # kudos:https://superfastpython.com/asyncio-cancel-task-and-wait/
            task = asyncio.current_task()
            if task and task.cancelled():
                raise
        self._listener_task = None

    async def subscribe(self, topic: str, qos: int | None = None) -> None:
        """Subscribe to an additional MQTT topic.

        Args:
            topic: The topic to subscribe to
            qos: Quality of Service level, uses config.qos if None

        """
        qos = qos or self.config.qos
        self.topics.append(topic)
        await self._client.subscribe(topic, qos)

    @retry(every=1, catch=MqttError, logger_fn=logger.exception)
    async def _run(self) -> None:
        """Background task for MQTT connection."""
        tls_params = (
            aiomqtt.TLSParameters(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            if self.config.ssl or self.config.port == 8883  # noqa: PLR2004
            else None
        )

        async with Client(
            hostname=self.config.host,
            port=self.config.port,
            username=self.config.user,
            password=self.config.password,
            timeout=self.config.timeout,
            keepalive=self.config.keep_alive,
            will=self.config.will,
            tls_params=tls_params,
        ) as client:
            self._client = client
            logger.info("subscribing to %(topics)s", {"topics": self.topics})
            await client.subscribe([(topic, self.config.qos) for topic in self.topics])

            async for message in client.messages:
                await self._message_queue.put(message)
