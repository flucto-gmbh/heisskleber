# Reference

## Baseclasses

```{eval-rst}
.. autoclass:: heisskleber.Sender
   :members:

.. autoclass:: heisskleber.Receiver
   :members:
```

## Serialization

See <project:serialization.md> for a tutorial on how to implement custom packer and unpacker for (de-)serialization.

```{eval-rst}
.. autoclass:: heisskleber.core::Packer

.. autoclass:: heisskleber.core::Unpacker
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

.. autoclass:: heisskleber.mqtt.MqttSender
    :members: send

.. autoclass:: heisskleber.mqtt.MqttReceiver
    :members: receive, subscribe

.. autoclass:: heisskleber.mqtt.MqttConf
    :members:
```

### ZMQ

```{eval-rst}
.. autoclass:: heisskleber.zmq::ZmqConf
```

```{eval-rst}
.. autoclass:: heisskleber.zmq::ZmqSender
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.zmq::ZmqReceiver
   :members: receive
```

### Serial

```{eval-rst}
.. autoclass:: heisskleber.serial::SerialConf
```

```{eval-rst}
.. autoclass:: heisskleber.serial::SerialSender
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.serial::SerialReceiver
   :members: receive
```

### TCP

```{eval-rst}
.. autoclass:: heisskleber.tcp::TcpConf
```

```{eval-rst}
.. autoclass:: heisskleber.tcp::TcpSender
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.tcp::TcpReceiver
   :members: receive
```

### UDP

```{eval-rst}
.. autoclass:: heisskleber.udp::UdpConf
```

```{eval-rst}
.. autoclass:: heisskleber.udp::UdpSender
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.udp::UdpReceiver
   :members: receive
```

### File

```{eval-rst}
.. autoclass:: heisskleber.file::FileConf
```

```{eval-rst}
.. autoclass:: heisskleber.file::FileWriter
   :members: send
```

```{eval-rst}
.. autoclass:: heisskleber.file::FileReader
   :members: receive
```
