from heisskleber import get_publisher, get_subscriber
from heisskleber.config import load_config

from .config import MqttConf


def map_topic(zmq_topic: str, mapping: str) -> str:
    return mapping + zmq_topic


def main() -> None:
    config: MqttConf = load_config(MqttConf(), "mqtt")
    sub = get_subscriber("zmq", config.topics)
    pub = get_publisher("mqtt")

    pub.pack = lambda x: x  # type: ignore
    sub.unpack = lambda x: x  # type: ignore

    while True:
        (zmq_topic, data) = sub.receive()
        mqtt_topic = map_topic(zmq_topic, config.mapping)

        pub.send(data, mqtt_topic)
