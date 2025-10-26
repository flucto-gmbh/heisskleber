import asyncio
import json
from urllib.request import Request, urlopen

import pytest

from heisskleber.core.unpacker import JSONUnpacker
from heisskleber.http.config import HTTPConf
from heisskleber.http.receiver import POSTReader


def _make_request(request: Request) -> tuple[int, bytes]:
    with urlopen(request, timeout=1) as resp:  # noqa: S310
        return resp.status, resp.read()


@pytest.mark.asyncio
async def test_post_reader() -> None:
    port = 8080
    url_path = "/"
    config = HTTPConf(port=port, url_path=url_path)
    reader = POSTReader(config=config, unpacker=JSONUnpacker())

    data = {"a": "b"}
    req = Request(f"http://localhost:{port}{url_path}", data=json.dumps(data).encode())
    req.add_header("Content-Type", "application/json")

    async with reader:
        status, msg = await asyncio.to_thread(_make_request, req)
        received = await reader.receive()

    assert status == 200
    assert msg == b"Received data."

    assert len(received) == 2
    assert received[0] == data
    assert received[1] == {}
