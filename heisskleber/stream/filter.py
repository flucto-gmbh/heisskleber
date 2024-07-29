from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from heisskleber.core import AsyncSource


class Filter(ABC):
    def __init__(self, source: AsyncSource):
        self.source = source

    async def __aiter__(self) -> AsyncGenerator[Any, None]:
        async for topic, data in self.source:
            data = self._filter(data)
            yield topic, data

    @abstractmethod
    def _filter(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
