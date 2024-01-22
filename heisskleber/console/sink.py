import json
import sys
import time
from typing import TextIO

from heisskleber.core.types import AsyncSink, Serializable, Sink


def pretty_print(data: dict[str, Serializable]) -> str:
    return json.dumps(data, indent=4)


class ConsoleSink(Sink):
    def __init__(self, stream: TextIO = sys.stdout, pretty: bool = False):
        self.stream = stream
        self.print = pretty_print if pretty else json.dumps

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        self.stream.write(self.print(data))  # type: ignore[operator]
        self.stream.write("\n")


class AsyncConsoleSink(AsyncSink):
    def __init__(self, stream: TextIO = sys.stdout, pretty: bool = False):
        self.stream = stream
        self.print = pretty_print if pretty else json.dumps

    async def send(self, data: dict[str, Serializable], topic: str) -> None:
        self.stream.write(self.print(data))  # type: ignore[operator]
        self.stream.write("\n")


if __name__ == "__main__":
    sink = ConsoleSink()
    while True:
        sink.send({"test": "test"}, "test")
        time.sleep(1)
