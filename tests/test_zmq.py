import time
from multiprocessing import Process
from pathlib import Path
from unittest.mock import patch

import pytest

from heisskleber import get_sink, get_source
from heisskleber.broker.zmq_broker import zmq_broker
from heisskleber.config import load_config
from heisskleber.zmq.config import ZmqConf
from heisskleber.zmq.publisher import ZmqPublisher
from heisskleber.zmq.subscriber import ZmqSubscriber


@pytest.fixture
def start_broker():
    # setup broker
    with patch("heisskleber.config.parse.get_config_filepath", return_value=Path("tests/resources/zmq.yaml")):
        broker_config = load_config(ZmqConf(), "zmq", read_commandline=False)
        broker_process = Process(
            target=zmq_broker,
            args=(broker_config,),
        )
        # start broker
        broker_process.start()

        yield broker_process

        broker_process.terminate()


def test_config_parses_correctly():
    conf = ZmqConf(protocol="tcp", host="localhost", publisher_port=5555, subscriber_port=5556)
    assert conf.protocol == "tcp"
    assert conf.host == "localhost"
    assert conf.publisher_port == 5555
    assert conf.subscriber_port == 5556

    assert conf.publisher_address == "tcp://localhost:5555"
    assert conf.subscriber_address == "tcp://localhost:5556"


def test_instantiate_subscriber():
    conf = ZmqConf(protocol="tcp", host="localhost", publisher_port=5555, subscriber_port=5556)
    sub = ZmqSubscriber(conf, "test")
    assert sub.config == conf


def test_instantiate_publisher():
    conf = ZmqConf(protocol="tcp", host="localhost", publisher_port=5555, subscriber_port=5556)
    pub = ZmqPublisher(conf)
    assert pub.config == conf


def test_send_receive(start_broker):
    print("test_send_receive")
    topic = "test"
    source = get_source("zmq", topic)
    source.start()
    sink = get_sink("zmq")
    sink.start()
    time.sleep(1)  # this is crucial, otherwise the source might hang
    for i in range(10):
        message = {"m": i}
        sink.send(message, topic)
        print(f"sent {topic} {message}")
        t, m = source.receive()
        print(f"received {t} {m}")
        assert t == topic
        assert m == {"m": i}
