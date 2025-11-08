import asyncio
import json
from typing import Literal, TypedDict
from urllib.request import Request, urlopen

import pytest
from pytest_httpserver import HTTPServer, RequestMatcher

from heisskleber.core.packer import JSONPacker
from heisskleber.http.config import HTTPConf
from heisskleber.http.sender import GETSender, POSTSender


class MatchArgs(TypedDict):
    uri: str
    method: Literal["POST"]
    json: dict[str, str]


@pytest.mark.asyncio
async def test_post_sender(httpserver: HTTPServer) -> None:
    data = {"a": "b"}
    match_kwargs = MatchArgs(uri="/", method="POST", json=data)
    (httpserver.expect_oneshot_request(**match_kwargs).respond_with_data("OK", status=200))
    port = httpserver.port
    config = HTTPConf(host="localhost", port=port)
    sender = POSTSender(config=config, packer=JSONPacker())
    async with sender:
        await sender.send(data=data)

    httpserver.assert_request_made(RequestMatcher(**match_kwargs))


def _make_request(request: Request) -> tuple[int, bytes]:
    with urlopen(request, timeout=1) as resp:  # noqa: S310
        return resp.status, resp.read()


@pytest.mark.asyncio
async def test_get_sender() -> None:
    port = 8080
    url_path = "/"
    config = HTTPConf(port=port, url_path=url_path)
    sender = GETSender(config=config, packer=JSONPacker())

    data = {"a": "b"}
    req = Request(f"http://localhost:{port}{url_path}")

    async with sender:
        await sender.send(data=data)
        status, msg = await asyncio.to_thread(_make_request, req)

    assert status == 200
    assert msg == json.dumps({"a": "b"}).encode()
