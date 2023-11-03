import signal
import sys

import zmq

from heisskleber.config import load_config
from heisskleber.network.zmq.config import ZmqConf as BrokerConf


def signal_handler(sig, frame):
    print("msb_broker.py exit")
    sys.exit(0)


class BrokerBindingError(Exception):
    pass


def bind_socket(socket, address, socket_type, verbose=False):
    """Bind a ZMQ socket and handle errors."""
    if verbose:
        print(f"creating {socket_type} socket")
    try:
        socket.bind(address)
    except Exception as err:
        raise BrokerBindingError(f"failed to bind to {socket_type}: {err}") from err
    if verbose:
        print(f"successfully bound to {socket_type} socket: {address}")


def create_proxy(xpub, xsub, verbose=False):
    """Create a ZMQ proxy to connect XPUB and XSUB sockets."""
    if verbose:
        print("creating proxy")
    try:
        zmq.proxy(xpub, xsub)
    except Exception as err:
        raise BrokerBindingError(f"failed to create proxy: {err}") from err


def msb_broker(config: BrokerConf) -> None:
    """Start a zmq broker.

    Binds to a publisher and subscriber port, allowing many to many connections."""
    ctx = zmq.Context()

    xpub = ctx.socket(zmq.XPUB)
    xsub = ctx.socket(zmq.XSUB)

    try:
        bind_socket(xpub, config.publisher_address, "publisher", config.verbose)
        bind_socket(xsub, config.subscriber_address, "subscriber", config.verbose)
        create_proxy(xpub, xsub, config.verbose)
    except BrokerBindingError as e:
        print(e)
        sys.exit(-1)


def main() -> None:
    """Start a zmq broker, with a user specified configuration."""
    signal.signal(signal.SIGINT, signal_handler)
    broker_config = load_config(BrokerConf(), "zmq")
    msb_broker(broker_config)
