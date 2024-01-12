import sys

from heisskleber import get_source
from heisskleber.config import load_config
from heisskleber.mqtt import MqttConf, MqttPublisher


def map_topic(mapping, zmq_topic):
    return mapping + zmq_topic


def main():
    # zmq_conf = load_config(ZmqConf(), "zmq")
    # zmq_source = ZmqSubscriber(zmq_conf, "")
    zmq_source = get_source("zmq", "")

    mqtt_conf = load_config(MqttConf(), "mqtt")
    mqtt_sink = MqttPublisher(mqtt_conf)
    # not sure if this works?
    # mqtt_sink.pack = lambda x: x
    # zmq_source.unpack = lambda x: x
    try:
        while True:
            topic, data = zmq_source.receive()
            mqtt_sink.send(data, map_topic(mqtt_conf.mapping, topic))
    except KeyboardInterrupt:
        print("received SIGINT, bye")
        sys.exit(0)


if __name__ == "__main__":
    main()
