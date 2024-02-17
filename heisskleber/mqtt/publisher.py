from __future__ import annotations

from heisskleber.core.packer import get_packer
from heisskleber.core.types import Serializable, Sink

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

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        if not self.client.is_connected():
            self.start()

        self._raise_if_thread_died()

        payload = self.pack(data)
        self.client.publish(topic, payload, qos=self.config.qos, retain=self.config.retain)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    def start(self) -> None:
        super().start()

    def stop(self) -> None:
        super().stop()
