import os

from heisskleber.config import BaseConf, load_config
from heisskleber.mqtt import AsyncMqttPublisher, AsyncMqttSubscriber, MqttConf
from heisskleber.zmq import ZmqAsyncPublisher, ZmqAsyncSubscriber, ZmqConf

from .types import AsyncSink, AsyncSource

_registered_async_sinks: dict[str, tuple[type[AsyncSink], type[BaseConf]]] = {
    "mqtt": (AsyncMqttPublisher, MqttConf),
    "zmq": (ZmqAsyncPublisher, ZmqConf),
}

_registered_async_sources: dict[str, tuple] = {
    "mqtt": (AsyncMqttSubscriber, MqttConf),
    "zmq": (ZmqAsyncSubscriber, ZmqConf),
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

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

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

    if "MSB_CONFIG_DIR" in os.environ:
        print(f"loading {name} config")
        config = load_config(conf_cls(), name, read_commandline=False)
    else:
        print(f"using default {name} config")
        config = conf_cls()

    return sub_cls(config, topic)
