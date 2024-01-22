import json
from unittest.mock import AsyncMock

import pytest

from heisskleber.mqtt import AsyncMqttSubscriber
from heisskleber.mqtt.config import MqttConf


class MockAsyncClient:
    def __init__(self):
        self.messages = AsyncMock()
        self.messages.return_value = [{"epoch": i, "data": 1} for i in range(10)]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def subscribe(self, *args):
        pass


@pytest.fixture
def mock_client():
    return MockAsyncClient()


@pytest.fixture
def mock_queue():
    return AsyncMock()


@pytest.mark.asyncio
async def test_subscribe_topics_single(mock_queue):
    mock_client = AsyncMock()
    config = MqttConf()
    topics = "single_topic"
    sub = AsyncMqttSubscriber(config, topics)
    sub.client = mock_client
    sub.message_queue = mock_queue

    await sub._subscribe_topics()

    mock_client.subscribe.assert_called_once_with(topics, config.qos)


@pytest.mark.asyncio
async def test_subscribe_topics_multiple(mock_queue):
    mock_client = AsyncMock()
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
