import argparse

from heisskleber import get_sink
from heisskleber.console.source import ConsoleSource


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="stdin")
    parser.add_argument("--dry-run", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()
    source = ConsoleSource()
    sink = get_sink("zmq")
    while True:
        topic, line = source.receive()
        print(f"{topic}: {line}")
        if not args.dry_run:
            sink.send(line, args.topic)


if __name__ == "__main__":
    main()
