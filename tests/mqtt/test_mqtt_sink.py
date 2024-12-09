import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

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
        await sink.send(test_data, test_topic)

        await asyncio.sleep(0.1)

        mock_client.publish.assert_awaited_once_with(topic=test_topic, payload=mock_packer.return_value)

        await sink.stop()
