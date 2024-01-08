import argparse
import sys
from typing import Union

from heisskleber import get_source
from heisskleber.console.sink import ConsoleSink

TopicType = Union[str, list[str]]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, choices=["zmq", "mqtt", "serial"], default="zmq")
    parser.add_argument("--topic", type=str, default="#")

    return parser.parse_args()


def main():
    args = parse_args()
    source = get_source(args.type, args.topic)
    sink = ConsoleSink()

    while True:
        topic, data = source.receive()
        sink.send(data, topic)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
