import json
import sys

from heisskleber.config import load_config
from heisskleber.mqtt import MqttConf, MqttPublisher
from heisskleber.zmq import ZmqConf, ZmqSubscriber


def main():
    zmq_conf = load_config(ZmqConf(), "zmq")
    zmq_source = ZmqSubscriber(zmq_conf, "")

    mqtt_conf = load_config(MqttConf(), "mqtt")
    mqtt_sink = MqttPublisher(mqtt_conf)
    # not sure if this works?
    mqtt_sink.pack = lambda x: x
    zmq_source.unpack = lambda x: x

    try:
        while True:
            for topic, data in zmq_source.receive():
                mqtt_sink.send(data=json.loads(data), topic=topic)
    except KeyboardInterrupt:
        print("received SIGINT, bye")
        sys.exit(0)


if __name__ == "__main__":
    main()
