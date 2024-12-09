import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from heisskleber.zmq import ZmqConf, ZmqSender


@pytest.mark.asyncio
async def test_zmq_sink_send() -> None:
    mock_socket = AsyncMock()
    mock_context = Mock()
    mock_context.socket.return_value = mock_socket

    test_dict = {"message": "test"}
    test_topic = "test"

    with patch("zmq.asyncio.Context.instance", return_value=mock_context):
        zmq_sink = ZmqSender(ZmqConf(publisher_port=5555))
        await zmq_sink.send(test_dict, topic=test_topic)

        mock_socket.connect.assert_called_once_with(zmq_sink.config.publisher_address)
        mock_socket.send_multipart.assert_called_once_with([test_topic.encode(), json.dumps(test_dict).encode()])
