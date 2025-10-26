#  a sink interface that POSTs data
import asyncio
import logging
import sys
from typing import Any, TypeVar

import aiohttp
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from heisskleber.core import Packer, Sender
from heisskleber.core.packer import JSONPacker
from heisskleber.http.config import HTTPConf

__all__ = ["GETSender", "POSTSender"]

T = TypeVar("T")


logger = logging.getLogger("heisskleber.http")


class POSTSender(Sender[T]):
    """HTTP POST Sender."""

    def __init__(self, config: HTTPConf, packer: Packer[T]) -> None:
        self.config = config
        self.packer = packer
        self._session: aiohttp.ClientSession | None = None

    async def send(self, data: T, **kwargs: Any) -> None:
        """POST data to url."""
        # TODO headers?
        if self._session is None:
            await self.start()
        assert self._session is not None  # noqa: S101 to satisfy mypy
        payload = self.packer(data)
        url = f"{self.config.protocol}://{self.config.host}:{self.config.port}{self.config.url_path}"
        await self._session.post(url, data=payload)

    def __repr__(self) -> str:  # noqa: D105
        return f"{self.__class__.__name__}({self.config}, {self.packer})"

    async def start(self) -> None:
        """Setup session."""
        self._session = aiohttp.ClientSession()

    async def stop(self) -> None:
        """Close the session."""
        if self._session is not None:
            await self._session.close()


class GETSender(Sender[T]):
    """Asynchronous GET server."""

    def __init__(
        self,
        config: HTTPConf,
        packer: Packer[T],
    ) -> None:
        self.config = config
        self.packer = packer
        self._queue: asyncio.queues.Queue[str | bytes | bytearray] = asyncio.queues.Queue(
            maxsize=config.max_buffer_size
        )
        self._runner: web.AppRunner | None = None

    def __repr__(self) -> str:  # noqa: D105
        return f"{self.__class__.__name__}({self.config!r}. {self.packer!r})"

    async def _handle(self, _: Request) -> Response:
        # TODO handle params / headers?
        try:
            data = self._queue.get_nowait()
            self._queue.task_done()
        except asyncio.queues.QueueEmpty:
            return web.Response(text="No data available.", status=500)
        except asyncio.queues.QueueShutDown:  # type: ignore[attr-defined]
            return web.Response(text="Sender not ready or already stopped.", status=500)

        if isinstance(data, str):
            data = data.encode("utf-8")
        elif isinstance(data, bytearray):
            data = bytes(data)
        return web.Response(body=data, status=200)

    async def send(self, data: T, **kwargs: Any) -> None:
        """Queue data to be queried by GET request."""
        self._queue.put_nowait(self.packer(data))

    async def start(self) -> None:
        """Start the AppRunner to listen for GET requests."""
        app = web.Application()
        app.add_routes([web.get(self.config.url_path, self._handle)])
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


async def _try_out_post_sender() -> None:
    config = HTTPConf(host="localhost", port=8080)
    sender = POSTSender(config=config, packer=JSONPacker())
    async with sender:
        await sender.send(data={"a": "b"})


# python -m aiohttp.web -H localhost -P 8080 "heisskleber.http.sender:_debug_app"
def _debug_server(_: Any) -> web.Application:
    async def _handler(request: web.Request) -> web.Response:
        print(request)  # noqa: T201
        print(await request.read())  # noqa: T201
        return web.Response()

    app = web.Application()
    app.router.add_route("*", "/", _handler)
    return app


async def _try_out_get_sender() -> None:
    config = HTTPConf(host="localhost", port=8080)
    sender = GETSender(config=config, packer=JSONPacker())
    async with sender:
        await sender.send({"a": "b"})
        await sender._queue.join()


# curl --header "Content-Type: application/json" \
#   --request GET \
#   http://localhost:8080/?a=b


def _main() -> int:
    print("Select mode:")  # noqa: T201
    print("(1) PostSender")  # noqa: T201
    print("(2) GetSender")  # noqa: T201
    answer = input()
    match answer:
        case "1":
            run = _try_out_post_sender
        case "2":
            run = _try_out_get_sender
        case _:
            return 1

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    sys.exit(_main())
