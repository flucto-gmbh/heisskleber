import json
import socket
from unittest.mock import patch

import pytest

from heisskleber.udp.config import UdpConf
from heisskleber.udp.publisher import UdpPublisher
from heisskleber.udp.subscriber import UdpSubscriber


@pytest.fixture
def mock_socket():
    with patch("heisskleber.udp.publisher.socket.socket") as mock_socket:
        yield mock_socket


@pytest.fixture
def mock_conf():
    return UdpConf(host="127.0.0.1", port=12345, packer="json")


def test_connects_to_socket(mock_socket, mock_conf) -> None:
    pub = UdpPublisher(mock_conf)
    pub.start()

    # constructor was called
    mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_DGRAM)
    pub.stop()


def test_closes_socket(mock_socket, mock_conf) -> None:
    pub = UdpPublisher(mock_conf)
    pub.start()
    pub.stop()

    # instace was closed
    mock_socket.return_value.close.assert_called()


def test_packs_and_sends_message(mock_socket, mock_conf) -> None:
    pub = UdpPublisher(mock_conf)

    # explicitly define packer to be json.dumps
    assert pub.pack == json.dumps

    pub.send({"key": "val", "intkey": 1, "floatkey": 1.0}, "test")

    mock_socket.return_value.sendto.assert_called_with(
        b'{"key": "val", "intkey": 1, "floatkey": 1.0, "topic": "test"}',
        (str(mock_conf.host), mock_conf.port),
    )
    pub.stop()


def test_subscriber_receives_message_from_queue(mock_conf) -> None:
    sub = UdpSubscriber(mock_conf)

    test_topic, test_data = ("test", {"key": "val", "intkey": 1, "floatkey": 1.0})

    sub._queue.put((test_topic, test_data))

    topic, data = sub.receive()
    assert test_topic == topic
    assert test_data == data
    sub.stop()


@pytest.fixture
def udp_sub(mock_conf):
    sub = UdpSubscriber(mock_conf)
    sub.config.port = 12346  # explicitly set port to avoid conflicts
    sub.start()
    yield sub
    sub.stop()


def test_sends_message_between_pub_and_sub(udp_sub, mock_conf):
    pub = UdpPublisher(mock_conf)
    test_data = {"key": "val", "intkey": 1, "floatkey": 1.0}
    test_topic = "test_topic"

    # Need to copy the dict, because the publisher will mutate it
    pub.send(test_data.copy(), test_topic)
    topic, data = udp_sub.receive()
    assert test_topic == topic
    assert test_data == data
