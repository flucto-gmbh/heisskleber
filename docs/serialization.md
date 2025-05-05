# Serialization

## Implementing a custom Packer

The packer class is defined in heisskleber.core.packer.py as a Protocol [see PEP 544](https://peps.python.org/pep-0544/).

```python
    T = TypeVar("T", contravariant=True)

    class Packer(Protocol[T]):
        def __call__(self, data: T) -> bytes:
            pass
```

Users can create custom Packer classes with variable input data, either as callable classes, subclasses of the packer class or functions.
Please note, that to satisfy type checking engines, the argument must be named `data`, but being Python, it's obviously not enforced at runtime.
The AsyncSink's type is defined by the concrete packer implementation. So if your Packer packs strings to bytes, the AsyncSink will be of type `AsyncSink[str]`,
indicating that the send function takes strings only, see example below:

```python
    from heisskleber import MqttSink, MqttConf

    def string_packer(data: str) -> bytes:
        return data.encode("ascii")

    async def main():
        sink = MqttSink(MqttConf(), packer = string_packer)
        await sink.send("Hi there!") # This is fine
        await sink.send({"data": 3.14}) # Type checker will complain
```

Heisskleber comes with default packers, such as the JSON_Packer, which can be importet as json_packer from heisskleber.core and is the default value for most Sinks.

## Implementing a custom Unpacker

The unpacker's responsibility is creating usable data from serialized byte strings.
This may be a serialized json string which is unpacked into a dictionary, but could be anything the user defines.
In heisskleber.core.unpacker.py the Unpacker Protocol is defined.

```python
    class Unpacker(Protocol[T]):
        def __call__(self, payload: bytes) -> tuple[T, dict[str, Any]]:
            pass
```

Here, the payload is fixed to be of type bytes and the return type is a combination of a user-defined data type and a dictionary of meta-data.

```{eval-rst}
.. note::
Please Note: The extra dictionary may be updated by the Source, e.g. the MqttSource will add a "topic" field, received from the mqtt node.
```

The receive function of an AsyncSource object will have its return type informed by the signature of the unpacker.

```python
    from heisskleber import MqttSource, MqttConf
    import time

    def csv_unpacker(payload: bytes) -> tuple[list[str], dict[str, Any]]:
        # Unpack a utf-8 encoded csv string, such as b'1,42,3.14,100.0' to [1.0, 42.0, 3.14, 100.0]
        # Adds some exemplary meta data
        return [float(chunk) for chunk in payload.decode().split(",")], {"processed_at": time.time()}

    async def main():
        sub = MqttSource(MqttConf, unpacker = csv_unpacker)
        data, extra = await sub.receive()
        assert isinstance(data, list[str]) # passes
```

## Error handling

To be implemented...
