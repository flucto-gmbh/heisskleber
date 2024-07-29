import pytest

from heisskleber.mqtt import MqttConf, MqttSink


@pytest.mark.asyncio
async def test_mqtt_send_has_topic():
    config = MqttConf()
    pub = MqttSink(config)
    payload = {"epoch": 1}
    await pub.send(payload)


def string_packer(data: str) -> bytes:
    return data.encode("ascii")


async def main():
    sink = MqttSink(MqttConf(), packer=string_packer)
    await sink.send("Hi there!")  # This is fine
    await sink.send({"data": 3.14})  # Type checker will complain
