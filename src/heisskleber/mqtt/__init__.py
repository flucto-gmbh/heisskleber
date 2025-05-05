"""Async wrappers for mqtt functionality.

MQTT implementation is achieved via the `aiomqtt`_ package, which is an async wrapper around the `paho-mqtt`_ package.

.. _aiomqtt: https://github.com/mossblaser/aiomqtt
.. _paho-mqtt: https://github.com/eclipse/paho.mqtt.python
"""

from heisskleber.core import register

from .config import MqttConf
from .receiver import MqttReceiver
from .sender import MqttSender

register("mqtt", MqttSender, MqttReceiver, MqttConf)

__all__ = ["MqttConf", "MqttReceiver", "MqttSender"]
