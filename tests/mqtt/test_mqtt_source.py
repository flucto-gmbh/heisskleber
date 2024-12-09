from unittest.mock import AsyncMock, patch

import aiomqtt
import pytest

from heisskleber.core.unpacker import JSONUnpacker
from heisskleber.mqtt import MqttConf, MqttReceiver


@pytest.mark.asyncio
async def test_mqtt_source_receive_message() -> None:
    """Test successful message reception and unpacking"""

    # Mock MQTT client
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()

    with patch("aiomqtt.Client", return_value=mock_client):
        mqtt_source = MqttReceiver(config=MqttConf(), topic="test", unpacker=JSONUnpacker())

        test_payload = b'{"test":"data"}'
        test_topic = "test/topic"
        message = aiomqtt.Message(topic=test_topic, payload=test_payload, qos=0, retain=False, mid=1, properties=None)
        await mqtt_source._message_queue.put(message)

        data, extra = await mqtt_source.receive()

        assert data == {"test": "data"}
        assert "topic" in extra
        assert extra["topic"] == test_topic

        await mqtt_source.stop()
