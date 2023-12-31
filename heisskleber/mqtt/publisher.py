from __future__ import annotations

from typing import Any

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Sink

from .config import MqttConf
from .mqtt_base import MqttBase


class MqttPublisher(MqttBase, Sink):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MqttConf) -> None:
        super().__init__(config)
        self.pack = get_packer(config.packstyle)

    def send(self, data: dict[str, Any], topic: str) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        self._raise_if_thread_died()

        payload = self.pack(data)
        self.client.publish(topic, payload, qos=self.config.qos, retain=self.config.retain)
