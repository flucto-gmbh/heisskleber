# Reference

## Baseclasses

```{eval-rst}
.. autoclass:: heisskleber.core.AsyncSink
   :members:

.. autoclass:: heisskleber.core.AsyncSource
   :members:
```

## Serialization

See <project:serialization.md> for a tutorial on how to implement custom packer and unpacker for (de-)serialization.

```{eval-rst}
.. autoclass:: heisskleber.core::Packer

.. autoclass:: heisskleber.core::Unpacker

.. autoclass:: heisskleber.core.unpacker::JSONUnpacker

.. autoclass:: heisskleber.core.packer::JSONPacker
```

### Errors

```{eval-rst}
.. autoclass:: heisskleber.core::UnpackerError

.. autoclass:: heisskleber.core::PackerError
```

## Implementations (Adapters)

### MQTT

```{eval-rst}
.. automodule:: heisskleber.mqtt
    :no-members:

.. autoclass:: heisskleber.mqtt.MqttSink
    :members: send

.. autoclass:: heisskleber.mqtt.MqttSource
    :members: receive, subscribe

.. autoclass:: heisskleber.mqtt.MqttConf
    :members:
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
