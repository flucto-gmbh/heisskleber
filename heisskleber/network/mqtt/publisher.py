from __future__ import annotations

from heisskleber.config import load_config
from heisskleber.network.packer import get_packer
from heisskleber.network.pubsub.types import Publisher

from .config import MqttConf
from .mqtt_base import MQTT_Base


class MqttPublisher(MQTT_Base, Publisher):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MqttConf):
        super().__init__(config)
        self.pack = get_packer(config.packstyle)

    def send(self, topic: str | bytes, data: dict):
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        self._raise_if_thread_died()
        if isinstance(topic, bytes):
            topic = topic.decode()

        payload = self.pack(data)
        self.client.publish(
            topic, payload, qos=self.config.qos, retain=self.config.retain
        )


def get_mqtt_publisher() -> MqttPublisher:
    """
    Generate mqtt publisher with configuration from yaml file,
    falls back to default values if no config is found
    """
    import os

    if "MSB_CONFIG_DIR" in os.environ:
        print("loading mqtt config")
        config = load_config(MqttConf(), "mqtt", read_commandline=False)
    else:
        print("using default mqtt config")
        config = MqttConf()
    return MqttPublisher(config)


def get_default_publisher() -> MqttPublisher:
    """
    Generate mqtt publisher with configuration from yaml file,
    falls back to default values if no config is found

    Deprecated, use get_mqtt_publisher() instead
    """
    return get_mqtt_publisher()
