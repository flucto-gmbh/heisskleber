# Reference

## Baseclasses

```{eval-rst}
.. automodule:: heisskleber.core.sink
   :members:

.. automodule:: heisskleber.core.source
   :members:
```

## Serialization

See <project:serialization.md> for a tutorial on how to implement custom packer and unpacker for (de-)serialization.

```{eval-rst}
.. autoclass:: heisskleber.core.packer::Packer

.. autoclass:: heisskleber.core.unpacker::Unpacker

.. autoclass:: heisskleber.core.unpacker::JSONUnpacker

.. autoclass:: heisskleber.core.packer::JSONPacker
```

## Implementations (Adapters)

### MQTT

MQTT implementation is achieved via the [aiomqtt](https://github.com/mossblaser/aiomqtt) package, which is an async wrapper around the [paho-mqtt](https://github.com/eclipse/paho.mqtt.python) package.

```{eval-rst}
.. autoclass:: heisskleber.mqtt::MqttConf
```

```{eval-rst}
.. autoclass:: heisskleber.mqtt::MqttSink
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.mqtt::MqttSource
   :members: receive
```

### ZMQ

```{eval-rst}
.. autoclass:: heisskleber.zmq::ZmqConf
```

```{eval-rst}
.. autoclass:: heisskleber.zmq::ZmqSink
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.zmq::ZmqSource
   :members: receive
```

### Serial

```{eval-rst}
.. autoclass:: heisskleber.serial::SerialConf
```

```{eval-rst}
.. autoclass:: heisskleber.serial::SerialSink
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.serial::SerialSource
   :members: receive
```

### TCP

```{eval-rst}
.. autoclass:: heisskleber.tcp::TcpConf
```

```{eval-rst}
.. autoclass:: heisskleber.tcp::TcpSink
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.tcp::TcpSource
   :members: receive
```

### UDP

```{eval-rst}
.. autoclass:: heisskleber.udp::UdpConf
```

```{eval-rst}
.. autoclass:: heisskleber.udp::UdpSink
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.udp::UdpSource
   :members: receive
```
