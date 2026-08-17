import json
import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest

from heisskleber.zmq import ZmqConf, ZmqSender


@pytest.mark.asyncio
async def test_zmq_sink_send() -> None:
    mock_socket = AsyncMock()
    mock_socket.connect = Mock(return_value=None)
    mock_context = Mock()
    mock_context.socket.return_value = mock_socket

    test_dict = {"message": "test"}
    test_topic = "test"

    with patch("zmq.asyncio.Context.instance", return_value=mock_context):
        zmq_sink = ZmqSender(ZmqConf(publisher_port=5555))
        await zmq_sink.send(test_dict, topic=test_topic)

        mock_socket.connect.assert_called_once_with(zmq_sink.config.publisher_address)
        mock_socket.send_multipart.assert_called_once_with([test_topic.encode(), json.dumps(test_dict).encode()])


@pytest.mark.asyncio
async def test_zmq_sender_send_log_records_format(caplog: pytest.LogCaptureFixture) -> None:
    """All log records emitted during send() must format without raising.

    Regression test: send() logged with an invalid '%(payload)b' conversion,
    raising ValueError whenever DEBUG logging was enabled.
    """
    mock_socket = AsyncMock()
    mock_socket.connect = Mock(return_value=None)
    mock_context = Mock()
    mock_context.socket.return_value = mock_socket

    with patch("zmq.asyncio.Context.instance", return_value=mock_context):
        zmq_sink: ZmqSender[dict[str, str]] = ZmqSender(ZmqConf(publisher_port=5555))
        with caplog.at_level(logging.DEBUG, logger="heisskleber.zmq"):
            await zmq_sink.send({"message": "test"}, topic="test")

    assert caplog.records, "expected debug log records from send()"
    for record in caplog.records:
        record.getMessage()  # raises ValueError on malformed format strings
