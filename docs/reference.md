# Reference

## Network

```{eval-rst}
.. automodule:: heisskleber
   :members:
.. automodule:: heisskleber.mqtt
   :members:
.. automodule:: heisskleber.zmq
   :members:
.. automodule:: heisskleber.serial
   :members:
.. automodule:: heisskleber.config
   :members:
```

### Broker

```{eval-rst}
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
.. autoclass:: heisskleber.mqtt.config.MqttConf
.. autoclass:: heisskleber.zmq.config.ZmqConf
.. autoclass:: heisskleber.serial.config.SerialConf
```
