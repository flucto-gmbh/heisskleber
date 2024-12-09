import asyncio
import json
from typing import Any

import pytest
import serial

from heisskleber.serial import SerialConf, SerialReceiver, SerialSender


def serial_unpacker(payload: bytes) -> tuple[dict[str, Any], dict[str, Any]]:
    return (json.loads(payload), {})


def serial_packer(data: dict[str, Any]) -> bytes:
    return (json.dumps(data) + "\n").encode()


@pytest.mark.asyncio
async def test_serial_with_ser() -> None:
    writer_port, reader_port = "./writer", "./reader"
    await asyncio.sleep(1)
    conf = SerialConf(
        port=reader_port,
        baudrate=9600,
    )
    source = SerialReceiver(conf, unpack=serial_unpacker)

    await asyncio.sleep(0.1)

    writer = serial.Serial(port=writer_port, baudrate=9600)
    writer.write(b'{"data": "test"}\n')
    writer.flush()

    sink = SerialSender(SerialConf(port=writer_port, baudrate=9600), pack=serial_packer)
    await sink.send({"data": "test"})

    data, extra = await source.receive()
    assert data == {"data": "test"}
