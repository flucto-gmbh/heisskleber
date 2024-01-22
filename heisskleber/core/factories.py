from heisskleber.config import BaseConf, load_config
from heisskleber.core.types import Sink, Source
from heisskleber.mqtt import MqttConf, MqttPublisher, MqttSubscriber
from heisskleber.serial import SerialConf, SerialPublisher, SerialSubscriber
from heisskleber.udp import UdpConf, UdpPublisher, UdpSubscriber
from heisskleber.zmq import ZmqConf, ZmqPublisher, ZmqSubscriber

_registered_sinks: dict[str, tuple[type[Sink], type[BaseConf]]] = {
    "zmq": (ZmqPublisher, ZmqConf),
    "mqtt": (MqttPublisher, MqttConf),
    "serial": (SerialPublisher, SerialConf),
    "udp": (UdpPublisher, UdpConf),
}

_registered_sources: dict[str, tuple[type[Source], type[BaseConf]]] = {
    "zmq": (ZmqSubscriber, ZmqConf),
    "mqtt": (MqttSubscriber, MqttConf),
    "serial": (SerialSubscriber, SerialConf),
    "udp": (UdpSubscriber, UdpConf),
}


def get_sink(name: str) -> Sink:
    """
    Factory function to create a sink object.

    Parameters:
        name: Name of the sink to create.
        config: Configuration object to use for the sink.
    """

    if name not in _registered_sinks:
        error_message = f"{name} is not a registered Sink."
        raise KeyError(error_message)

    pub_cls, conf_cls = _registered_sinks[name]

    print(f"loading {name} config")
    config = load_config(conf_cls(), name, read_commandline=False)

    return pub_cls(config)


def get_source(name: str, topic: str | list[str]) -> Source:
    """
    Factory function to create a source object.

    Parameters:
        name: Name of the source to create.
        config: Configuration object to use for the source.
        topic: Topic to subscribe to.
    """

    if name not in _registered_sinks:
        error_message = f"{name} is not a registered Source."
        raise KeyError(error_message)

    sub_cls, conf_cls = _registered_sources[name]

    print(f"loading {name} config")
    config = load_config(conf_cls(), name, read_commandline=False)

    return sub_cls(config, topic)


def get_subscriber(name: str, topic: str | list[str]) -> Source:
    """
    Deprecated: Factory function to create a source object (formerly known as subscriber).

    Parameters:
        name: Name of the source to create.
        config: Configuration object to use for the source.
        topic: Topic to subscribe to.
    """

    print("Deprecated: use get_source instead.")
    return get_source(name, topic)


def get_publisher(name: str) -> Sink:
    """
    Deprecated: Factory function to create a sink object (formerly known as publisher).

    Parameters:
        name: Name of the sink to create.
        config: Configuration object to use for the sink.
    """

    print("Deprecated: use get_sink instead.")
    return get_sink(name)
