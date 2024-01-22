from unittest.mock import patch

import pytest

from heisskleber import get_publisher, get_sink, get_source, get_subscriber
from heisskleber.mqtt import MqttConf, MqttPublisher, MqttSubscriber
from heisskleber.serial import SerialConf, SerialPublisher, SerialSubscriber
from heisskleber.zmq import ZmqConf, ZmqPublisher, ZmqSubscriber


@pytest.fixture(autouse=True)
def mock_connections():
    with (
        patch("heisskleber.mqtt.mqtt_base.mqtt_client", autospec=True),
        patch("heisskleber.zmq.publisher.zmq.Context", autospec=True),
        patch("heisskleber.serial.subscriber.serial.Serial"),
    ):
        yield


@pytest.mark.skip
@pytest.mark.parametrize(
    "name,pubtype,conftype",
    [
        ("mqtt", MqttPublisher, MqttConf),
        ("zmq", ZmqPublisher, ZmqConf),
        ("serial", SerialPublisher, SerialConf),
    ],
)
def test_get_publisher(name, pubtype, conftype):
    pub = get_publisher(name)
    assert isinstance(pub, pubtype)
    assert isinstance(pub.config, conftype)


@pytest.mark.skip
@pytest.mark.parametrize(
    "name,subtype",
    [
        ("mqtt", MqttSubscriber),
        ("zmq", ZmqSubscriber),
        ("serial", SerialSubscriber),
    ],
)
def test_get_subscriber(name, subtype):
    sub = get_subscriber(name, "topic")
    assert isinstance(sub, subtype)


@pytest.mark.skip
@pytest.mark.parametrize(
    "name,sinktype",
    [
        ("mqtt", MqttPublisher),
        ("zmq", ZmqPublisher),
        ("serial", SerialPublisher),
    ],
)
def test_get_sink(name, sinktype):
    pub = get_sink(name)
    assert isinstance(pub, sinktype)


@pytest.mark.skip
@pytest.mark.parametrize(
    "name,sourcetype",
    [
        ("mqtt", MqttSubscriber),
        ("zmq", ZmqSubscriber),
        ("serial", SerialSubscriber),
    ],
)
def test_get_source(name, sourcetype):
    sub = get_source(name, "topic")
    assert isinstance(sub, sourcetype)
