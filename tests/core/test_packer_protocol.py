from heisskleber.core import Packer, Unpacker
from heisskleber.core.packer import JSONPacker
from heisskleber.mqtt.config import MqttConf
from heisskleber.zmq import ZmqSink
from heisskleber.mqtt import MqttSink
from typing import Callable, Any
import json


# packer : Callable[[dict[str, Any]], bytes] =
def json_packer(data: dict[str, Any]) -> bytes:
    return json.dumps(data).encode()


def float_packer(data: float) -> bytes:
    return str(data).encode()


async def test_packer_is_callable():
    config = MqttConf()
    pub = MqttSink(config, packer=float_packer)
    await pub.send(3.14)
