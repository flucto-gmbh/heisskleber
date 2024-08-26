import json

from heisskleber.core import AsyncSink


class ConsoleSink(AsyncSink[dict[str, int | float | str]]):
    def __init__(self, pretty: bool = False, verbose: bool = False) -> None:
        self.verbose = verbose
        self.pretty = pretty

    async def send(self, data: dict[str, int | float | str], topic: str | None = None, **kwargs) -> None:
        verbose_topic = topic + ":\t" if topic else ""
        if self.pretty:
            print(verbose_topic + json.dumps(data, indent=4))
        else:
            print(verbose_topic + str(data))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pretty={self.pretty}, verbose={self.verbose})"

    async def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
