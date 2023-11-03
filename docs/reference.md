# Reference

## Network

```{eval-rst}
.. automodule:: heisskleber.network
   :members:
.. automodule:: heisskleber.network.mqtt
.. autoclass:: MqttPublisher
.. autoclass:: MqttSubscriber
.. automodule:: heisskleber.network.zmq
   :members:
.. autoclass:: ZmqPublisher
.. autoclass:: ZmqSubscriber
```

### Broker

```{eval-rst}
.. automodule:: heisskleber.broker
    :members:
```

## Config

### Loading configs
```{eval-rst}
.. automodule:: heisskleber.config
   :members: load_config
```

### Config types

Configs are extended dataclasses, which inherit from the BaseConf class.
```{eval-rst}
.. autoclass:: heisskleber.config.BaseConf
.. autoclass:: heisskleber.network.mqtt.config.MqttConf
.. autoclass:: heisskleber.network.zmq.config.ZmqConf
.. autoclass:: heisskleber.network.serial.config.SerialConf
```
