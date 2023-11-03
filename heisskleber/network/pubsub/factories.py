import os

from heisskleber.config import load_config
from heisskleber.network.mqtt import MqttConf, MqttPublisher, MqttSubscriber
from heisskleber.network.serial import SerialConf, SerialPublisher, SerialSubscriber
from heisskleber.network.zmq import ZmqConf, ZmqPublisher, ZmqSubscriber

_registered_publishers = {
    "zmq": (ZmqPublisher, ZmqConf),
    "mqtt": (MqttPublisher, MqttConf),
    "serial": (SerialPublisher, SerialConf),
}

_registered_subscribers = {
    "zmq": (ZmqSubscriber, ZmqConf),
    "mqtt": (MqttSubscriber, MqttConf),
    "serial": (SerialSubscriber, SerialConf),
}


def get_publisher(name: str):
    if name not in _registered_publishers:
        error_message = f"{name} is not a registered Publisher."
        raise KeyError(error_message)

    pub_cls, conf_cls = _registered_publishers[name]

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

    return pub_cls(config)


def get_subscriber(name: str, topic):
    if name not in _registered_publishers:
        error_message = f"{name} is not a registered Subscriber."
        raise KeyError(error_message)

    sub_cls, conf_cls = _registered_subscribers[name]

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

    return sub_cls(topic, config)
