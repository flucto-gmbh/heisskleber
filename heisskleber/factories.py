from heisskleber.config import BaseConf, load_config
from heisskleber.core.sink import AsyncSink
from heisskleber.core.source import AsyncSource
from heisskleber.mqtt import MqttConf, MqttSink, MqttSource
from heisskleber.udp import UdpConf, UdpSink, UdpSource
from heisskleber.zmq import ZmqConf, ZmqSink, ZmqSource

_registered_async_sinks: dict[str, tuple[type[AsyncSink], type[BaseConf]]] = {
    "mqtt": (MqttSink, MqttConf),
    "zmq": (ZmqSink, ZmqConf),
    "udp": (UdpSink, UdpConf),
}

_registered_async_sources: dict[str, tuple] = {
    "mqtt": (MqttSource, MqttConf),
    "zmq": (ZmqSource, ZmqConf),
    "udp": (UdpSource, UdpConf),
}


def get_async_sink(name: str) -> AsyncSink:
    """
    Factory function to create a sink object.

    Parameters:
        name: Name of the sink to create.
        config: Configuration object to use for the sink.
    """

    if name not in _registered_async_sinks:
        error_message = f"{name} is not a registered Sink."
        raise KeyError(error_message)

    pub_cls, conf_cls = _registered_async_sinks[name]

    config = load_config(conf_cls(), name, read_commandline=False)

    return pub_cls(config)


def get_async_source(name: str, topic: str | list[str] | tuple[str]) -> AsyncSource:
    """
    Factory function to create a source object.

    Parameters:
        name: Name of the source to create.
        config: Configuration object to use for the source.
        topic: Topic to subscribe to.
    """

    if name not in _registered_async_sources:
        error_message = f"{name} is not a registered Source."
        raise KeyError(error_message)

    sub_cls, conf_cls = _registered_async_sources[name]

    config = load_config(conf_cls(), name, read_commandline=False)

    return sub_cls(config, topic)