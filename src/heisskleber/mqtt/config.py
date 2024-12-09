"""Mqtt config."""

from dataclasses import dataclass
from typing import Any

from aiomqtt import Will

from heisskleber.core import BaseConf


@dataclass
class WillConf(BaseConf):
    """MQTT Last Will and Testament message configuration."""

    topic: str
    payload: str | None = None
    qos: int = 0
    retain: bool = False

    def to_aiomqtt_will(self) -> Will:
        """Create an aiomqtt style will."""
        return Will(topic=self.topic, payload=self.payload, qos=self.qos, retain=self.retain, properties=None)


@dataclass
class MqttConf(BaseConf):
    """MQTT configuration class."""

    # transport
    host: str = "localhost"
    port: int = 1883
    ssl: bool = False

    # mqtt
    user: str = ""
    password: str = ""
    qos: int = 0
    retain: bool = False
    max_saved_messages: int = 100
    timeout: int = 60
    keep_alive: int = 60
    will: Will | None = None

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "MqttConf":
        """Create a MqttConf object from a dictionary."""
        if "will" in config_dict:
            config_dict = config_dict.copy()
            config_dict["will"] = WillConf.from_dict(config_dict["will"]).to_aiomqtt_will()
        return super().from_dict(config_dict)
