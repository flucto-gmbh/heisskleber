from dataclasses import dataclass, field

from heisskleber.config import BaseConf


@dataclass
class MqttConf(BaseConf):
    """
    MQTT configuration class.
    """

    packstyle: str = "json"

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

    # data
    topics: list[str] = field(default_factory=list)
