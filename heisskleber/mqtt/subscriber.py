from __future__ import annotations

from queue import SimpleQueue
from typing import Any

from paho.mqtt.client import MQTTMessage

from heisskleber.core.packer import get_unpacker
from heisskleber.core.types import Source

from .config import MqttConf
from .mqtt_base import MqttBase


class MqttSubscriber(MqttBase, Source):
    """
    MQTT subscriber, wraps around ecplipse's paho mqtt client.
    Network message loop is handled in a separated thread.

    Incoming messages are saved as a stack when not processed via the receive() function.
    """

    def __init__(self, config: MqttConf, topics: str | list[str]) -> None:
        super().__init__(config)
        self.topics = topics
        self._message_queue: SimpleQueue[MQTTMessage] = SimpleQueue()
        self.unpack = get_unpacker(config.packstyle)

    def subscribe(self, topics: str | list[str] | tuple[str]) -> None:
        """
        Subscribe to one or multiple topics
        """
        if isinstance(topics, (list, tuple)):
            # if subscribing to multiple topics, use a list of tuples
            subscription_list = [(topic, self.config.qos) for topic in topics]
            self.client.subscribe(subscription_list)
        else:
            self.client.subscribe(topics, self.config.qos)
        if self.config.verbose:
            print(f"Subscribed to: {topics}")

    def receive(self) -> tuple[str, dict[str, Any]]:
        """
        Reads a message from mqtt and returns it

        Messages are saved in a stack, if no message is available, this function blocks.

        Returns:
            tuple(topic: str, message: dict): the message received
        """
        if not self.client:
            self.start()

        self._raise_if_thread_died()
        mqtt_message = self._message_queue.get(block=True, timeout=self.config.timeout_s)

        message_returned = self.unpack(mqtt_message.payload.decode())
        return (mqtt_message.topic, message_returned)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    def start(self) -> None:
        super().start()
        self.subscribe(self.topics)
        self.client.on_message = self._on_message
        self.is_connected = True

    def stop(self) -> None:
        super().stop()

    # callback to add incoming messages onto stack
    def _on_message(self, client, userdata, message) -> None:
        self._message_queue.put(message)

        if self.config.verbose:
            print(f"Topic: {message.topic}")
            print(f"MQTT message: {message.payload.decode()}")
