from heisskleber.config import load_config
from heisskleber.network import get_publisher, get_subscriber

from .config import MqttConf


def map_topic(zmq_topic, mapping):
    return mapping + zmq_topic.decode()


def main():
    config: MqttConf = load_config(MqttConf(), "mqtt")
    sub = get_subscriber("zmq", config.topics)
    pub = get_publisher("mqtt")

    sub.unpack = pub.pack = lambda x: x

    while True:
        (zmq_topic, data) = sub.receive()
        mqtt_topic = map_topic(zmq_topic, config.mapping)

        pub.send(mqtt_topic, data)
