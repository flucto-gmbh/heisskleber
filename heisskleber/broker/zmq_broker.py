import sys

import zmq
from zmq import Socket

from heisskleber.config import load_config
from heisskleber.zmq.config import ZmqConf as BrokerConf


class BrokerBindingError(Exception):
    pass


def bind_socket(socket: Socket, address: str, socket_type: str, verbose=False) -> None:
    """Bind a ZMQ socket and handle errors."""
    if verbose:
        print(f"creating {socket_type} socket")
    try:
        socket.bind(address)
    except Exception as err:
        error_message = f"failed to bind to {socket_type}: {err}"
        raise BrokerBindingError(error_message) from err
    if verbose:
        print(f"successfully bound to {socket_type} socket: {address}")


def create_proxy(xpub: Socket, xsub: Socket, verbose=False) -> None:
    """Create a ZMQ proxy to connect XPUB and XSUB sockets."""
    if verbose:
        print("creating proxy")
    try:
        zmq.proxy(xpub, xsub)
    except Exception as err:
        error_message = f"failed to create proxy: {err}"
        raise BrokerBindingError(error_message) from err


# TODO reimplement as object?
def zmq_broker(config: BrokerConf) -> None:
    """Start a zmq broker.

    Binds to a publisher and subscriber port, allowing many to many connections."""
    ctx = zmq.Context()

    xpub = ctx.socket(zmq.XPUB)
    xsub = ctx.socket(zmq.XSUB)

    try:
        bind_socket(xpub, config.subscriber_address, "publisher", config.verbose)
        bind_socket(xsub, config.publisher_address, "subscriber", config.verbose)
        create_proxy(xpub, xsub, config.verbose)
    except BrokerBindingError as e:
        print(e)
        sys.exit(-1)


def main() -> None:
    """Start a zmq broker, with a user specified configuration."""
    broker_config = load_config(BrokerConf(), "zmq")
    zmq_broker(broker_config)
