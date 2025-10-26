#  a sink interface that POSTs data
import asyncio
import logging
from typing import Any, TypeVar

import aiohttp
from aiohttp import web

from heisskleber.core import Packer, Sender
from heisskleber.core.packer import JSONPacker
from heisskleber.http.config import HTTPConf

__all__ = ["POSTSender"]

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

    def __repr__(self) -> str:
        """Return string representation of the HTTP POST sink object."""
        return f"{self.__class__.__name__}({self.config}, {self.packer})"

    async def start(self) -> None:
        """Setup session."""
        self._session = aiohttp.ClientSession()

    async def stop(self) -> None:
        """Close the session."""
        if self._session is not None:
            await self._session.close()


async def _try_out() -> None:
    config = HTTPConf(host="localhost", port=8080)
    sender = POSTSender(config=config, packer=JSONPacker())
    async with sender:
        await sender.send(data={"a": "b"})


# python -m aiohttp.web -H localhost -P 8080 "heisskleber.http.sender:_debug_app"
def _debug_app(_: Any) -> web.Application:
    async def _handler(request: web.Request) -> web.Response:
        print(request)  # noqa: T201
        print(await request.read())  # noqa: T201
        return web.Response()

    app = web.Application()
    app.router.add_route("*", "/", _handler)
    return app


if __name__ == "__main__":
    asyncio.run(_try_out())
