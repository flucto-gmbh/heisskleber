import json
import time

from heisskleber.core.types import AsyncSink, Serializable, Sink


class ConsoleSink(Sink):
    def __init__(self, pretty: bool = False, verbose: bool = False) -> None:
        self.verbose = verbose
        self.pretty = pretty

    def send(self, data: dict[str, Serializable], topic: str) -> None:
        verbose_topic = topic + ":\t" if self.verbose else ""
        if self.pretty:
            print(verbose_topic + json.dumps(data, indent=4))
        else:
            print(verbose_topic + str(data))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pretty={self.pretty}, verbose={self.verbose})"

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class AsyncConsoleSink(AsyncSink):
    def __init__(self, pretty: bool = False, verbose: bool = False) -> None:
        self.verbose = verbose
        self.pretty = pretty

    async def send(self, data: dict[str, Serializable], topic: str) -> None:
        verbose_topic = topic + ":\t" if self.verbose else ""
        if self.pretty:
            print(verbose_topic + json.dumps(data, indent=4))
        else:
            print(verbose_topic + str(data))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pretty={self.pretty}, verbose={self.verbose})"

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


if __name__ == "__main__":
    sink = ConsoleSink()
    while True:
        sink.send({"test": "test"}, "test")
        time.sleep(1)
