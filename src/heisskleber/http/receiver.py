# a source that returns POSTed data
import asyncio
import logging
import sys
from collections.abc import Mapping
from typing import Any, TypeVar

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from heisskleber.core import Receiver, Unpacker
from heisskleber.core.unpacker import JSONUnpacker
from heisskleber.http.config import HTTPConf

__all__ = ["GETReader", "POSTReader"]


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
        self._runner: web.AppRunner | None = None

    def __repr__(self) -> str:  # noqa: D105
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
        """Start the AppRunner to listen for POST requests."""
        app = web.Application()
        app.add_routes([web.post(self.config.url_path, self._handle)])
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.config.host, self.config.port)
        await site.start()

    async def stop(self) -> None:
        """Stop the AppRunner."""
        if self._runner is not None:
            await self._runner.cleanup()
            try:
                async with asyncio.timeout(5):
                    await self._queue.join()
            except asyncio.TimeoutError:
                pass
            finally:
                self._queue.shutdown(immediate=True)  # type: ignore[attr-defined]


class GETReader(Receiver[T]):
    """Asynchronous GET source."""

    def __init__(
        self,
        config: HTTPConf,
        unpacker: Unpacker[T],
    ) -> None:
        self.config = config
        self.unpacker = unpacker
        self._session: aiohttp.ClientSession | None = None

    def __repr__(self) -> str:  # noqa: D105
        return f"{self.__class__.__name__}({self.config!r}. {self.unpacker!r})"

    async def receive(self, params: Mapping[str, str] | None = None, **kwargs: Any) -> tuple[T, dict[str, Any]]:
        """Get the next data."""
        if self._session is None:
            await self.start()
        assert self._session is not None  # noqa: S101 to satisfy mypy
        url = f"{self.config.protocol}://{self.config.host}:{self.config.port}{self.config.url_path}"
        response = await self._session.get(url, params=params)
        response.raise_for_status()
        data, extra = self.unpacker(await response.read())
        return data, extra

    async def start(self) -> None:
        """Setup session."""
        self._session = aiohttp.ClientSession()

    async def stop(self) -> None:
        """Close the session."""
        if self._session is not None:
            await self._session.close()


async def _try_out_post_reader() -> None:
    config = HTTPConf(host="localhost", port=8080)
    reader = POSTReader(config=config, unpacker=JSONUnpacker())
    async with reader:
        print(await reader.receive())  # noqa: T201


# curl --header "Content-Type: application/json" \
#   --request POST \
#   --data '{"username":"xyz","password":"xyz"}' \
#   http://localhost:8080/


async def _try_out_get_reader() -> None:
    config = HTTPConf(host="localhost", port=8080)
    reader = GETReader(config=config, unpacker=JSONUnpacker())
    async with reader:
        print(await reader.receive(params={"a": "b"}))  # noqa: T201


# python -m aiohttp.web -H localhost -P 8080 "heisskleber.http.receiver:_debug_app"
def _debug_server(_: Any) -> web.Application:
    async def _handler(request: web.Request) -> web.Response:
        print(request)  # noqa: T201
        print(await request.read())  # noqa: T201
        return web.json_response({"Hello": "World"}, status=200)

    app = web.Application()
    app.router.add_route("*", "/", _handler)
    return app


def _main() -> int:
    print("Select mode:")  # noqa: T201
    print("(1) PostReader")  # noqa: T201
    print("(2) GetReader")  # noqa: T201
    answer = input()
    match answer:
        case "1":
            run = _try_out_post_reader
        case "2":
            run = _try_out_get_reader
        case _:
            return 1

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    sys.exit(_main())
