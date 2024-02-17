from unittest.mock import Mock, patch

import pytest
import serial

from heisskleber.core.packer import serialpacker
from heisskleber.serial.config import SerialConf
from heisskleber.serial.publisher import SerialPublisher
from heisskleber.serial.subscriber import SerialSubscriber


@pytest.fixture
def serial_conf():
    return SerialConf(port="/dev/test", baudrate=9600, bytesize=8, verbose=False)


@pytest.fixture
def mock_serial_device_subscriber():
    with patch("heisskleber.serial.subscriber.serial.Serial") as mock:
        yield mock


@pytest.fixture
def mock_serial_device_publisher():
    with patch("heisskleber.serial.publisher.serial.Serial") as mock:
        yield mock


def test_serial_subscriber_initialization(mock_serial_device_subscriber, serial_conf):
    """Test that the SerialSubscriber class initializes correctly.
    Mocks the serial.Serial class to avoid opening a serial port."""
    _ = SerialSubscriber(
        config=serial_conf,
        topic="",
    )
    mock_serial_device_subscriber.assert_called_with(
        port=serial_conf.port,
        baudrate=serial_conf.baudrate,
        bytesize=serial_conf.bytesize,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )


def test_serial_subscriber_receive(mock_serial_device_subscriber, serial_conf):
    """Test that the SerialSubscriber class calls readline and unpack as expected."""
    subscriber = SerialSubscriber(config=serial_conf, topic="")

    # Set up the readline return value
    mock_serial_instance = mock_serial_device_subscriber.return_value
    mock_serial_instance.readline.return_value = b"test message\n"

    # Set up the unpack function to convert message to dict
    unpack_func = Mock(return_value={"data": "test message"})
    subscriber.unpack = unpack_func

    # Call the receive method and assert it behaves as expected
    _, payload = subscriber.receive()

    # Was readline called?
    mock_serial_instance.readline.assert_called_once()

    # Was unpack called?
    assert payload == {"data": "test message"}
    unpack_func.assert_called_once_with("test message\n")


def test_serial_subscriber_converts_bytes_to_str():
    """Test that the SerialSubscriber class converts bytes to str as expected."""
    with patch("heisskleber.serial.subscriber.serial.Serial") as mock_serial:
        subscriber = SerialSubscriber(config=SerialConf(), topic="", custom_unpack=lambda x: x)

        # Set the readline method to raise UnicodeError
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.readline.side_effect = [b"test message", b"test\x86more"]

        _, payload = subscriber.receive()
        assert payload == "test message"

        # Assert that none-unicode is skipped
        _, payload = subscriber.receive()
        assert payload == "testmore"


def test_serial_publisher_initialization(mock_serial_device_publisher, serial_conf):
    """Test that the SerialPublisher class initializes correctly.
    Mocks the serial.Serial class to avoid opening a serial port."""
    publisher = SerialPublisher(config=serial_conf)
    mock_serial_device_publisher.assert_called_with(
        port=serial_conf.port,
        baudrate=serial_conf.baudrate,
        bytesize=serial_conf.bytesize,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )
    assert publisher.serial_connection


def test_serial_publisher_send(mock_serial_device_publisher, serial_conf):
    """Test that the SerialPublisher class calls write and pack as expected."""
    publisher = SerialPublisher(config=serial_conf)

    # Set up the readline return value
    mock_serial_instance = mock_serial_device_publisher.return_value
    mock_serial_instance.readline.return_value = b"test message\n"

    # Set up the pack function to convert dict to comma separated string of values
    publisher.pack = serialpacker

    # Call the receive method and assert it behaves as expected
    publisher.send({"data": "test message", "more_data": "more message"}, "test")

    # Was write called with encoded payload?
    mock_serial_instance.write.assert_called_once_with(b"test message,more message")
    mock_serial_instance.flush.assert_called_once()
