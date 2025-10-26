from typing import Literal, TypedDict

import pytest
from pytest_httpserver import HTTPServer, RequestMatcher

from heisskleber.core.packer import JSONPacker
from heisskleber.http.config import HTTPConf
from heisskleber.http.sender import POSTSender


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
