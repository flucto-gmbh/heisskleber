import json
from typing import Any

from heisskleber.core.types import AsyncSink


class AsyncConsoleSink(AsyncSink):
    def __init__(self, pretty: bool = False, verbose: bool = False) -> None:
        self.verbose = verbose
        self.pretty = pretty

    async def send(self, data: dict[str, Any], topic: str) -> None:
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
