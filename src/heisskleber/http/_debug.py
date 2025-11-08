# ruff: noqa: T201 D415
import asyncio
import sys
from typing import Any

from aiohttp import web

from heisskleber.core.packer import JSONPacker
from heisskleber.core.unpacker import JSONUnpacker
from heisskleber.http.config import HTTPConf
from heisskleber.http.receiver import GETReader, POSTReader
from heisskleber.http.sender import GETSender, POSTSender


def debug_server(_: Any) -> web.Application:
    """Start from commandline:

    python -m aiohttp.web -H localhost -P 8080 "heisskleber.http._debug:debug_server"
    """

    async def handle_get(request: web.Request) -> web.Response:
        print(request)
        print(await request.read())
        return web.json_response({"Hello": "World"}, status=200)

    async def handle_post(request: web.Request) -> web.Response:
        print(request)
        print(await request.read())
        return web.Response()

    app = web.Application()
    app.router.add_route("GET", "/", handle_get)
    app.router.add_route("POST", "/", handle_post)
    return app


async def debug_get_reader() -> None:
    """Make sure debug_server is running before running this."""
    config = HTTPConf(host="localhost", port=8080)
    reader = GETReader(config=config, unpacker=JSONUnpacker())
    async with reader:
        print(await reader.receive(params={"a": "b"}))


async def debug_post_sender() -> None:
    """Make sure debug_server is running before running this."""
    config = HTTPConf(host="localhost", port=8080)
    sender = POSTSender(config=config, packer=JSONPacker())
    async with sender:
        await sender.send(data={"a": "b"})


_GET_SENDER_CURL = 'curl --header "Content-Type: application/json" --request GET  "http://localhost:8080/"'


async def debug_get_sender() -> None:
    """Query with e.g. curl:

    curl --header "Content-Type: application/json" \
    --request GET \
    http://localhost:8080/
    """
    config = HTTPConf(host="localhost", port=8080)
    sender = GETSender(config=config, packer=JSONPacker())
    async with sender:
        await sender.send({"a": "b"})
        await sender._queue.join()


_POST_READER_CURL = """curl --header "Content-Type: application/json" --request POST --data '{"username":"xyz","password":"xyz"}' http://localhost:8080/"""


async def debug_post_reader() -> None:
    """Query with e.g. curl:

    curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"username":"xyz","password":"xyz"}' \
    http://localhost:8080/
    """
    config = HTTPConf(host="localhost", port=8080)
    reader = POSTReader(config=config, unpacker=JSONUnpacker())
    async with reader:
        print(await reader.receive())


def main() -> int:
    print("Select mode:")
    print("Requiring running debug server:")
    print('python -m aiohttp.web -H localhost -P 8080 "heisskleber.http._debug:debug_server"')
    print("(1) GetReader")
    print("(2) PostSender")
    print("Query using e.g. curl:")
    print("(3) GetSender")
    print("(4) PostReader")
    answer = input()
    match answer:
        case "1":
            run = debug_get_reader
        case "2":
            run = debug_post_sender
        case "3":
            run = debug_get_sender
            print(_GET_SENDER_CURL)
        case "4":
            run = debug_post_reader
            print(_POST_READER_CURL)
        case _:
            return 1

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    sys.exit(main())
