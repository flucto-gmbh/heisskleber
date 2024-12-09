import asyncio
import contextlib
import logging
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio

from heisskleber.tcp import TcpConf, TcpReceiver


def bytes_csv_unpacker(payload: bytes) -> tuple[dict[str, Any], dict[str, Any]]:
    """Unpack string containing comma separated values to dictionary."""
    vals = payload.decode().rstrip().split(",")
    keys = [f"key{i}" for i in range(len(vals))]
    return (dict(zip(keys, vals)), {"topic": "tcp"})


port = 23456
tcp_logger_name = "heisskleber.tcp"


class TcpTestSender:
    server: asyncio.Server

    def __init__(self):
        self.on_connected = self._send_ok

    async def start(self, port):
        self.server = await asyncio.start_server(self.handle_connection, port=port)

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()

    def handle_connection(self, _reader, writer):
        self.on_connected(writer)

    def _send_ok(self, writer):
        writer.write(b"OK\n")


@pytest_asyncio.fixture
# @pytest.mark.asyncio(loop_scope="session")
async def sender() -> AsyncGenerator[TcpTestSender, None]:
    sender = TcpTestSender()
    yield sender
    await sender.stop()


@pytest.fixture
def mock_conf():
    return TcpConf(host="127.0.0.1", port=port, restart_behavior=TcpConf.RestartBehavior.NEVER)


def test_00_bytes_csv_unpacker() -> None:
    unpacker = bytes_csv_unpacker
    data, extra = unpacker(b"OK")
    assert data == {"key0": "OK"}
    assert extra == {"topic": "tcp"}


@pytest.mark.asyncio
async def test_01_connect_refused(mock_conf, caplog) -> None:
    logger = logging.getLogger(tcp_logger_name)
    logger.setLevel(logging.WARNING)

    source = TcpReceiver(mock_conf)
    with contextlib.suppress(ConnectionRefusedError):
        await source.start()

    assert len(caplog.record_tuples) == 1
    logger_name, level, message = caplog.record_tuples[0]
    assert logger_name == "heisskleber.tcp"
    assert level == 40
    assert message == f"TcpReceiver(host=127.0.0.1, port={port}): ConnectionRefusedError"
    await source.stop()


@pytest.mark.asyncio
async def test_02_connect_timedout(mock_conf, caplog) -> None:
    logger = logging.getLogger("heisskleber.tcp")
    logger.setLevel(logging.WARNING)

    mock_conf.timeout = 1
    source = TcpReceiver(mock_conf)
    # Linux "ConnectionRefusedError", Windows says "TimeoutError"
    with contextlib.suppress(TimeoutError, ConnectionRefusedError):
        await source.start()
    assert len(caplog.record_tuples) == 1
    logger_name, level, message = caplog.record_tuples[0]
    assert logger_name == tcp_logger_name
    assert level == 40
    assert message in (
        f"TcpReceiver(host=127.0.0.1, port={port}): ConnectionRefusedError",
        f"TcpReceiver(host=127.0.0.1, port={port}): TimeoutError",
    )
    await source.stop()


@pytest.mark.asyncio
async def test_03_connect_retry(mock_conf, caplog, sender) -> None:
    logger = logging.getLogger(tcp_logger_name)
    logger.setLevel(logging.INFO)

    mock_conf.timeout = 1
    mock_conf.restart_behavior = "always"
    source = TcpReceiver(mock_conf)
    start_task = asyncio.create_task(source.start())

    async def delayed_start():
        await asyncio.sleep(1.2)
        await sender.start(mock_conf.port)

    await asyncio.create_task(delayed_start())
    await start_task
    assert len(caplog.record_tuples) >= 3
    logger_name, level, message = caplog.record_tuples[-1]
    assert logger_name == tcp_logger_name
    assert level == 20
    assert message == f"TcpReceiver(host=127.0.0.1, port={port}) connected successfully!"
    await source.stop()


@pytest.mark.asyncio
async def test_04_connects_to_socket(mock_conf, caplog, sender) -> None:
    logger = logging.getLogger(tcp_logger_name)
    logger.setLevel(logging.INFO)

    await sender.start(mock_conf.port)

    source = TcpReceiver(mock_conf)
    await source.start()
    assert len(caplog.record_tuples) == 2
    logger_name, level, message = caplog.record_tuples[0]
    assert logger_name == tcp_logger_name
    assert level == 20
    assert message == f"TcpReceiver(host=127.0.0.1, port={port}) waiting for connection."
    logger_name, level, message = caplog.record_tuples[1]
    assert logger_name == tcp_logger_name
    assert level == 20
    assert message == f"TcpReceiver(host=127.0.0.1, port={port}) connected successfully!"
    await source.stop()


@pytest.mark.asyncio
async def test_05_connection_to_server_lost(mock_conf, sender) -> None:
    def test_steps():
        # First connection: close it
        writer = yield
        writer.close()

        # Second connection: send data
        writer = yield
        writer.write(b"OK after second connect\n")

    connection_handler = test_steps()  # construct the generator
    next(connection_handler)  # prime the generator

    def handle_incoming_connection(writer):
        connection_handler.send(writer)

    sender.on_connected = handle_incoming_connection

    await sender.start(mock_conf.port)

    source = TcpReceiver(mock_conf, unpacker=bytes_csv_unpacker)
    data = await source.receive()
    _check_data(data, "OK after second connect")
    await source.stop()


@pytest.mark.asyncio
async def test_06_data_received(mock_conf, sender) -> None:
    await sender.start(mock_conf.port)

    source = TcpReceiver(mock_conf, unpacker=bytes_csv_unpacker)
    data = await source.receive()
    _check_data(data, "OK")
    await source.stop()


def _check_data(data, expected_value: str):
    assert isinstance(data, tuple)
    assert len(data) == 2
    result, extra = data
    assert result == {"key0": expected_value}
    assert isinstance(result, dict)
    assert "key0" in result
