import json
from queue import SimpleQueue
from unittest.mock import call, patch

import pytest
from paho.mqtt.client import MQTTMessage

from heisskleber.mqtt.config import MqttConf
from heisskleber.mqtt.mqtt_base import MqttBase
from heisskleber.mqtt.subscriber import MqttSubscriber


# Mock configuration for MQTT_Base
@pytest.fixture
def mock_mqtt_conf() -> MqttConf:
    return MqttConf(
        broker="localhost",
        port=1883,
        user="user",
        password="passwd",  # noqa: S106, this is a test password
        ssl=False,
        verbose=False,
        qos=1,
    )


# Mock the paho mqtt client
@pytest.fixture
def mock_mqtt_client():
    with patch("heisskleber.mqtt.mqtt_base.mqtt_client", autospec=True) as mock:
        yield mock


@pytest.fixture
def mock_queue():
    with patch("heisskleber.mqtt.subscriber.SimpleQueue", spec=SimpleQueue) as mock:
        yield mock


def test_mqtt_base_intialization(mock_mqtt_client, mock_mqtt_conf):
    """Test that the intialization of the mqtt client is as expected."""
    base = MqttBase(config=mock_mqtt_conf)

    mock_mqtt_client.assert_called_once()
    mock_mqtt_client.return_value.loop_start.assert_called_once()
    mock_client_instance = mock_mqtt_client.return_value
    mock_client_instance.username_pw_set.assert_called_with(mock_mqtt_conf.user, mock_mqtt_conf.password)
    mock_client_instance.connect.assert_called_with(mock_mqtt_conf.broker, mock_mqtt_conf.port)
    assert base.client.on_connect == base._on_connect
    assert base.client.on_disconnect == base._on_disconnect
    assert base.client.on_publish == base._on_publish
    assert base.client.on_message == base._on_message


def test_mqtt_base_on_connect(mock_mqtt_client, mock_mqtt_conf, capsys):
    base = MqttBase(config=mock_mqtt_conf)
    base._on_connect(None, None, {}, 0)
    captured = capsys.readouterr()
    assert f"MQTT node connected to {mock_mqtt_conf.broker}:{mock_mqtt_conf.port}" in captured.out


def test_mqtt_base_on_disconnect_with_error(mock_mqtt_client, mock_mqtt_conf, capsys):
    """Assert that the mqtt client shuts down when disconnect callback is received."""
    base = MqttBase(config=mock_mqtt_conf)
    with pytest.raises(SystemExit):
        base._on_disconnect(None, None, 1)
    captured = capsys.readouterr()
    assert "Killing this service" in captured.out
    print(captured.out)


def test_mqtt_subscribes_single_topic(mock_mqtt_client, mock_mqtt_conf):
    """Test that the mqtt client subscribes to a single topic."""
    _ = MqttSubscriber(topics="singleTopic", config=mock_mqtt_conf)

    actual_calls = mock_mqtt_client.return_value.subscribe.call_args_list
    assert actual_calls == [call("singleTopic", mock_mqtt_conf.qos)]


def test_mqtt_subscribes_multiple_topics(mock_mqtt_client, mock_mqtt_conf):
    """Test that the mqtt client subscribes to multiple topics passed as list.

    I would love to do this via parametrization, but the call argument is built differently for single size lists and longer lists.
    """
    _ = MqttSubscriber(topics=["multiple1", "multiple2"], config=mock_mqtt_conf)

    actual_calls = mock_mqtt_client.return_value.subscribe.call_args_list
    assert actual_calls == [
        call([("multiple1", mock_mqtt_conf.qos), ("multiple2", mock_mqtt_conf.qos)]),
    ]


def test_mqtt_subscribes_multiple_topics_tuple(mock_mqtt_client, mock_mqtt_conf):
    """Test that the mqtt client subscribes to multiple topics passed as tuple."""
    _ = MqttSubscriber(topics=("multiple1", "multiple2"), config=mock_mqtt_conf)

    actual_calls = mock_mqtt_client.return_value.subscribe.call_args_list
    assert actual_calls == [
        call([("multiple1", mock_mqtt_conf.qos), ("multiple2", mock_mqtt_conf.qos)]),
    ]


def create_fake_mqtt_message(topic: bytes, payload: bytes) -> MQTTMessage:
    msg = MQTTMessage()
    msg.topic = topic
    msg.payload = payload
    return msg


def test_receive_with_message(mock_mqtt_conf: MqttConf, mock_mqtt_client, mock_queue):
    """Test the mqtt receive function with fake MQTT messages."""
    topic = b"test/topic"
    payload = json.dumps({"key": "value"}).encode()
    fake_message = create_fake_mqtt_message(topic, payload)

    mock_queue.return_value.get.side_effect = [fake_message]
    subscriber = MqttSubscriber(topics=[topic.decode()], config=mock_mqtt_conf)

    received_topic, received_payload = subscriber.receive()

    assert received_topic == "test/topic"
    assert received_payload == {"key": "value"}


def test_message_is_put_into_queue(mock_mqtt_conf: MqttConf, mock_mqtt_client, mock_queue):
    """Test that values a put into a queue when on_message callback is called."""
    topic = b"test/topic"
    payload = json.dumps({"key": "value"}).encode()
    fake_message = create_fake_mqtt_message(topic, payload)

    mock_queue.return_value.get.side_effect = [fake_message]
    subscriber = MqttSubscriber(topics=[topic.decode()], config=mock_mqtt_conf)

    subscriber._on_message(None, None, fake_message)

    mock_queue.return_value.put.assert_called_once_with(fake_message)


def test_message_is_put_into_queue_with_actual_queue(mock_mqtt_conf, mock_mqtt_client):
    """Test that the buffering via queue works as expected."""
    topic = b"test/topic"
    payload = json.dumps({"key": "value"}).encode()
    fake_message = create_fake_mqtt_message(topic, payload)

    # mock_queue.return_value.get.side_effect = [fake_message]
    subscriber = MqttSubscriber(topics=[topic.decode()], config=mock_mqtt_conf)

    subscriber._on_message(None, None, fake_message)

    topic, return_dict = subscriber.receive()

    assert topic == "test/topic"
    assert return_dict == {"key": "value"}
