from unittest.mock import AsyncMock, patch

from heisskleber.mqtt import AsyncMqttPublisher, MqttConf


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


def test_repr_mqtt() -> None:
    with patch("heisskleber.mqtt.publisher_async.aiomqtt.Client") as client:
        client.return_value = MockAsyncClient()
        config = MqttConf(
            broker="localhost",
            port=1883,
            user="testuser",
            password="test",  # noqa: S106, this is a test
            qos=2,
            packstyle="json",
        )
        pub = AsyncMqttPublisher(config)
        assert (
            repr(pub)
            == "AsyncMqttPublisher(broker=localhost, port=1883, user=testuser, password=****, qos=2, packstyle=json)"
        )
