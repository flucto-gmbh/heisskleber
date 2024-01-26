import argparse
import sys
from typing import Union

from heisskleber.config import load_config
from heisskleber.console.sink import ConsoleSink
from heisskleber.core.factories import _registered_sources

TopicType = Union[str, list[str]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, choices=["zmq", "mqtt", "serial", "udp"], default="zmq")
    parser.add_argument("--topic", type=str, default="#")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=1883)

    return parser.parse_args()


def run() -> None:
    args = parse_args()
    # source = get_source(args.type, args.topic)
    sink = ConsoleSink()

    sub_cls, conf_cls = _registered_sources[args.type]

    try:
        config = load_config(conf_cls(), args.type, read_commandline=False)
    except FileNotFoundError:
        print(f"Using default config for {args.type}.")
        config = conf_cls()

    if args.port:
        config.port = args.port

    if args.host:
        if args.type == "mqtt":
            config.broker = args.host
        elif args.type == "zmq":
            config.interface = args.host
        elif args.type == "udp":
            config.ip = args.host

    if args.type == "zmq" and args.topic == "#":
        args.topic = ""

    source = sub_cls(config, args.topic)
    while True:
        topic, data = source.receive()
        sink.send(data, topic)


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
