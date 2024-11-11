from dataclasses import dataclass

from heisskleber.core import BaseConf


@dataclass
class MqttConf(BaseConf):
    """
    MQTT configuration class.
    """

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
    timeout_s: int = 60
