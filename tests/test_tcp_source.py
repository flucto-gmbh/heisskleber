import asyncio
import contextlib
import logging

import pytest
import pytest_asyncio

from heisskleber.tcp.config import TcpConf
from heisskleber.tcp.source import TcpSource


class TcpTestSender:
    def __init__(self):
        self.server = None
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
async def test_sender():
    sender = TcpTestSender()
    yield sender
    await sender.stop()


@pytest.fixture
def mock_conf():
    return TcpConf(host="127.0.0.1", port=12345, restart_behavior=TcpConf.RestartBehavior.NEVER)


@pytest.mark.asyncio
async def test_01_connect_refused(mock_conf, caplog) -> None:
    logger = logging.getLogger("AsyncTcpSource")
    logger.setLevel(logging.WARNING)

    source = TcpSource(mock_conf, None)
    with contextlib.suppress(ConnectionRefusedError):
        await source.start()
    assert len(caplog.record_tuples) == 1
    logger_name, level, message = caplog.record_tuples[0]
    assert logger_name == "AsyncTcpSource"
    assert level == 40
    assert message == "AsyncTcpSource(host=127.0.0.1, port=12345): ConnectionRefusedError"
    source.stop()


@pytest.mark.asyncio
async def test_02_connect_timedout(mock_conf, caplog) -> None:
    logger = logging.getLogger("AsyncTcpSource")
    logger.setLevel(logging.WARNING)

    mock_conf.timeout = 1
    source = TcpSource(mock_conf, None)
    # Linux "ConnectionRefusedError", Windows says "TimeoutError"
    with contextlib.suppress(TimeoutError, ConnectionRefusedError):
        await source.start()
    assert len(caplog.record_tuples) == 1
    logger_name, level, message = caplog.record_tuples[0]
    assert logger_name == "AsyncTcpSource"
    assert level == 40
    assert (
        message == "AsyncTcpSource(host=127.0.0.1, port=12345): ConnectionRefusedError"
        or message == "AsyncTcpSource(host=127.0.0.1, port=12345): TimeoutError"
    )
    source.stop()


@pytest.mark.asyncio
async def test_03_connect_retry(mock_conf, caplog, test_sender) -> None:
    logger = logging.getLogger("AsyncTcpSource")
    logger.setLevel(logging.INFO)

    mock_conf.timeout = 1
    mock_conf.restart_behavior = TcpConf.RestartBehavior.INFINITELY
    source = TcpSource(mock_conf, None)
    source.start()

    async def delayed_start():
        await asyncio.sleep(1.2)
        await test_sender.start(mock_conf.port)

    await asyncio.create_task(delayed_start())
    await source.start()
    assert len(caplog.record_tuples) >= 3
    logger_name, level, message = caplog.record_tuples[-1]
    assert logger_name == "AsyncTcpSource"
    assert level == 20
    assert message == "AsyncTcpSource(host=127.0.0.1, port=12345) connected successfully!"
    source.stop()


@pytest.mark.asyncio
async def test_04_connects_to_socket(mock_conf, caplog, test_sender) -> None:
    logger = logging.getLogger("AsyncTcpSource")
    logger.setLevel(logging.INFO)

    await test_sender.start(mock_conf.port)

    source = TcpSource(mock_conf, None)
    await source.start()
    assert len(caplog.record_tuples) == 2
    logger_name, level, message = caplog.record_tuples[0]
    assert logger_name == "AsyncTcpSource"
    assert level == 20
    assert message == "AsyncTcpSource(host=127.0.0.1, port=12345) waiting for connection."
    logger_name, level, message = caplog.record_tuples[1]
    assert logger_name == "AsyncTcpSource"
    assert level == 20
    assert message == "AsyncTcpSource(host=127.0.0.1, port=12345) connected successfully!"
    source.stop()


@pytest.mark.asyncio
async def test_05_connection_to_server_lost(mock_conf, caplog, test_sender) -> None:
    def test_steps():
        # First connection: close it
        writer = yield
        writer.close()

        # Second connection: send data
        writer = yield
        writer.write(b"OK after second connect\n")

    connection_handler = test_steps()
    next(connection_handler)

    def handle_incoming_connection(writer):
        connection_handler.send(writer)

    test_sender.on_connected = handle_incoming_connection

    await test_sender.start(mock_conf.port)

    source = TcpSource(mock_conf, None)
    data = await source.receive()
    _check_data(data, "OK after second connect")
    source.stop()


@pytest.mark.asyncio
async def test_06_data_received(mock_conf, caplog, test_sender) -> None:
    await test_sender.start(mock_conf.port)

    source = TcpSource(mock_conf, None)
    data = await source.receive()
    _check_data(data, "OK")
    source.stop()


def _check_data(data, expected_value: str):
    assert isinstance(data, tuple)
    assert len(data) == 2
    assert data[0] == "tcp"
    assert isinstance(data[1], dict)
    result = data[1]
    assert "key0" in result
    assert result["key0"] == expected_value
