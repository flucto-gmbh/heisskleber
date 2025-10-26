# a source that returns POSTed data
import asyncio
import logging
from typing import Any, TypeVar

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from heisskleber.core import Receiver, Unpacker
from heisskleber.core.unpacker import JSONUnpacker
from heisskleber.http.config import HTTPConf

__all__ = ["POSTReader"]


T = TypeVar("T")
logger = logging.getLogger("heisskleber.http")


class POSTReader(Receiver[T]):
    """Asynchronous POST source."""

    def __init__(
        self,
        config: HTTPConf,
        unpacker: Unpacker[T],
    ) -> None:
        self.config = config
        self.unpacker = unpacker
        self._queue: asyncio.queues.Queue[bytes] = asyncio.queues.Queue(maxsize=config.max_buffer_size)

    def __repr__(self) -> str:
        """Return string representation of HTTP Source class."""
        return f"{self.__class__.__name__}({self.config!r}. {self.unpacker!r})"

    async def _handle(self, request: Request) -> Response:
        data = await request.read()
        if not len(data):
            return web.Response(text="Empty Body send.", status=400)

        try:
            self._queue.put_nowait(data)
        except asyncio.queues.QueueFull:
            return web.Response(text="Queue is full. Try again later.", status=507)
        except asyncio.queues.QueueShutDown:  # type: ignore[attr-defined]
            return web.Response(text="Receiver not ready or already stopped.", status=500)

        return web.Response(text="Received data.", status=200)

    async def receive(self, **kwargs: Any) -> tuple[T, dict[str, Any]]:
        """Get the next data."""
        data, extra = self.unpacker(await self._queue.get())
        self._queue.task_done()
        return data, extra

    async def start(self) -> None:
        """Start the AppRunner to listen for GET requests."""
        app = web.Application()
        app.add_routes([web.post(self.config.url_path, self._handle)])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.config.host, self.config.port)
        await self.site.start()

    async def stop(self) -> None:
        """Stop the AppRunner."""
        await self.runner.cleanup()
        try:
            async with asyncio.timeout(5):
                await self._queue.join()
        except asyncio.TimeoutError:
            pass
        finally:
            self._queue.shutdown(immediate=True)  # type: ignore[attr-defined]


async def _try_out() -> None:
    config = HTTPConf(host="localhost", port=8080)
    reader = POSTReader(config=config, unpacker=JSONUnpacker())
    async with reader:
        print(await reader.receive())  # noqa: T201


# curl --header "Content-Type: application/json" \
#   --request POST \
#   --data '{"username":"xyz","password":"xyz"}' \
#   http://localhost:8080/

if __name__ == "__main__":
    asyncio.run(_try_out())
