import os
import signal
import threading

import pytest

from heisskleber.broker import zmq_broker


def timeout_handler(signum, frame):
    os.kill(os.getpid(), signal.SIGINT)


@pytest.fixture
def limit_execution_time():
    # Set the timeout duration (in seconds)
    timeout_duration = 10  # for example, 5 seconds

    # Set up the timer
    timer = threading.Timer(timeout_duration, lambda: timeout_handler(None, None))
    timer.start()

    yield

    # Cancel the timer if the test finishes in time
    timer.cancel()


def test_broker(limit_execution_time):
    zmq_broker.main()
