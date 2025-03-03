import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from heisskleber.core import PackerError
from heisskleber.mqtt import MqttConf, MqttSender


@pytest.mark.asyncio
async def test_send_work_successful_publish() -> None:
    """Test successful message publishing"""
    mqtt_config = MqttConf()
    mock_packer = Mock(return_value=b'{"test": "data"}')
    sink = MqttSender(config=mqtt_config, packer=mock_packer)

    # Mock MQTT client
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()

    with patch("aiomqtt.Client", return_value=mock_client):
        test_data = {"test": "data"}
        test_topic = "test/topic"
        await sink.send(test_data, test_topic, qos=2, retain=True)

        await asyncio.sleep(0.1)

        mock_client.publish.assert_awaited_once_with(
            topic=test_topic, payload=mock_packer.return_value, qos=2, retain=True
        )

        await sink.stop()


@pytest.mark.asyncio
async def test_mqtt_send_raises_error() -> None:
    class ErrorPacker:
        def __call__(self, data: str) -> bytes:
            raise PackerError(data)

    mqtt_config = MqttConf()
    sink = MqttSender(config=mqtt_config, packer=ErrorPacker())
    test_data = "test"
    test_topic = "test/topic"

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()

    with patch("aiomqtt.Client", return_value=mock_client):
        with pytest.raises(PackerError):
            await sink.send(test_data, test_topic)

        await sink.stop()


@pytest.mark.asyncio
async def test_mqtt_max_queue_size() -> None:
    mqtt_config = MqttConf(max_saved_messages=2)

    sink = MqttSender(config=mqtt_config)
    sink._sender_task = True  # Skip connection

    for v in ["first", "second", "third"]:
        await sink.send({"value": v}, topic="test")

    assert sink._send_queue.qsize() == 2

    second_value, _, _, _ = sink._send_queue.get_nowait()
    third_value, _, _, _ = sink._send_queue.get_nowait()

    assert json.loads(third_value)["value"] == "third"
    assert json.loads(second_value)["value"] == "second"

    assert sink._send_queue.empty()
