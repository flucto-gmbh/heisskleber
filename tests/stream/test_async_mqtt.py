import json
from unittest.mock import AsyncMock

import pytest

from heisskleber.mqtt import AsyncMqttSubscriber
from heisskleber.mqtt.config import MqttConf


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def mock_queue():
    return AsyncMock()


@pytest.mark.asyncio
async def test_subscribe_topics_single(mock_client, mock_queue):
    config = MqttConf()
    topics = "single_topic"
    sub = AsyncMqttSubscriber(config, topics)
    sub.client = mock_client
    sub.message_queue = mock_queue

    await sub._subscribe_topics()

    mock_client.subscribe.assert_called_once_with(topics, config.qos)


@pytest.mark.asyncio
async def test_subscribe_topics_multiple(mock_client, mock_queue):
    config = MqttConf()
    topics = ["topic1", "topic2"]
    sub = AsyncMqttSubscriber(config, topics)
    sub.client = mock_client
    sub.message_queue = mock_queue

    await sub._subscribe_topics()

    mock_client.subscribe.assert_called_once_with([(t, config.qos) for t in topics])


@pytest.mark.asyncio
async def test_receive(mock_client, mock_queue):
    config = MqttConf()
    sub = AsyncMqttSubscriber(config, "some_topic")
    sub.client = mock_client
    sub.message_queue = mock_queue

    mock_message = AsyncMock()
    mock_message.topic = "some_topic"
    mock_message.payload = json.dumps({"some": "payload"}).encode("utf-8")

    mock_queue.get.return_value = mock_message

    topic, payload = await sub.receive()

    assert isinstance(topic, str)
    assert topic == mock_message.topic
    assert payload == {"some": "payload"}
