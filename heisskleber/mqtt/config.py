from dataclasses import dataclass, field

from heisskleber.config import BaseConf


@dataclass
class MqttConf(BaseConf):
    """
    MQTT configuration class.
    """

    host: str = "localhost"
    user: str = ""
    password: str = ""
    port: int = 1883
    ssl: bool = False
    qos: int = 0
    retain: bool = False
    topics: list[str] = field(default_factory=list)
    mapping: str = "/msb/"
    packstyle: str = "json"
    max_saved_messages: int = 100
    timeout_s: int = 60
