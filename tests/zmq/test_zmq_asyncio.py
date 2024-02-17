import time
from collections.abc import Generator
from multiprocessing import Process
from unittest.mock import patch

import pytest

from heisskleber.broker.zmq_broker import zmq_broker
from heisskleber.config import load_config
from heisskleber.zmq.config import ZmqConf
from heisskleber.zmq.publisher import ZmqAsyncPublisher, ZmqPublisher
from heisskleber.zmq.subscriber import ZmqAsyncSubscriber


@pytest.fixture
def start_broker() -> Generator[Process, None, None]:
    # setup broker
    with patch(
        "heisskleber.config.parse.get_config_filepath",
        return_value="tests/resources/zmq.yaml",
    ):
        broker_config = load_config(ZmqConf(), "zmq", read_commandline=False)
        broker_process = Process(
            target=zmq_broker,
            args=(broker_config,),
        )
        # start broker
        broker_process.start()

        yield broker_process

        broker_process.terminate()


def test_instantiate_subscriber() -> None:
    conf = ZmqConf(protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556)
    sub = ZmqAsyncSubscriber(conf, "test")
    assert sub.config == conf


def test_instantiate_publisher() -> None:
    conf = ZmqConf(protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556)
    pub = ZmqPublisher(conf)
    assert pub.config == conf


@pytest.mark.asyncio
async def test_send_receive(start_broker) -> None:
    print("test_send_receive")
    topic = "test"
    conf = ZmqConf(protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556)
    source = ZmqAsyncSubscriber(conf, topic)
    sink = ZmqAsyncPublisher(conf)
    source.start()
    sink.start()
    time.sleep(1)  # this is crucial, otherwise the source might hang
    for i in range(10):
        message = {"m": i}
        await sink.send(message, topic)
        print(f"sent {topic} {message}")
        t, m = await source.receive()
        print(f"received {t} {m}")
        assert t == topic
        assert m == {"m": i}
