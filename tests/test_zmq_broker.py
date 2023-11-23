import os
import signal
import threading
from unittest.mock import patch

import pytest

from heisskleber.broker import zmq_broker
from heisskleber.zmq import ZmqConf


def timeout_handler(signum, frame):
    os.kill(os.getpid(), signal.SIGINT)


@pytest.fixture
def limit_execution_time():
    # Set the timeout duration (in seconds)
    timeout_duration = 3  # for example, 5 seconds

    # Set up the timer
    timer = threading.Timer(timeout_duration, lambda: timeout_handler(None, None))
    timer.start()

    yield

    # Cancel the timer if the test finishes in time
    timer.cancel()


@pytest.fixture
def mock_load_config():
    with patch("heisskleber.broker.zmq_broker.load_config") as mock_load:
        mock_load.return_value = ZmqConf()
        yield mock_load


def test_broker_sigint(limit_execution_time, mock_load_config):
    zmq_broker.main()


def test_broker_run(limit_execution_time):
    broker_conf = ZmqConf()
    zmq_broker.zmq_broker(config=broker_conf)
