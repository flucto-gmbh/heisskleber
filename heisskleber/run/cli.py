import argparse
import sys
from typing import Callable, Union

from heisskleber.config import load_config
from heisskleber.console.sink import ConsoleSink
from heisskleber.core.factories import _registered_sources
from heisskleber.mqtt import MqttSubscriber
from heisskleber.udp import UdpSubscriber
from heisskleber.zmq import ZmqSubscriber


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="hkcli",
        description="Heisskleber command line interface",
        usage="%(prog)s [options]",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=["zmq", "mqtt", "serial", "udp"],
        default="zmq",
    )
    parser.add_argument(
        "-T",
        "--topic",
        type=str,
        default="#",
        help="Topic to subscribe to, valid for zmq and mqtt only.",
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        help="Host or broker for MQTT, zmq and UDP.",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        help="Port or serial interface for MQTT, zmq and UDP.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-p", "--pretty", action="store_true", help="Pretty print JSON data.")

    return parser.parse_args()


def keyboardexit(func) -> Callable:
    def wrapper(*args, **kwargs) -> Union[None, int]:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)

    return wrapper


@keyboardexit
def main() -> None:
    args = parse_args()
    sink = ConsoleSink(pretty=args.pretty, verbose=args.verbose)

    sub_cls, conf_cls = _registered_sources[args.type]

    try:
        config = load_config(conf_cls(), args.type, read_commandline=False)
    except FileNotFoundError:
        print(f"No config file found for {args.type}, using default values and user input.")
        config = conf_cls()

    source = sub_cls(config, args.topic)
    if isinstance(source, (MqttSubscriber, UdpSubscriber)):
        source.config.host = args.host or source.config.host
        source.config.port = args.port or source.config.port
    elif isinstance(source, ZmqSubscriber):
        source.config.host = args.host or source.config.host
        source.config.subscriber_port = args.port or source.config.subscriber_port
        source.topic = "" if args.topic == "#" else args.topic
    elif isinstance(source, UdpSubscriber):
        source.config.port = args.port or source.config.port

    source.start()
    sink.start()

    while True:
        topic, data = source.receive()
        sink.send(data, topic)


if __name__ == "__main__":
    main()
