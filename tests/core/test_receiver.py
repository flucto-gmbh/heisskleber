from typing import Any

import pytest

from heisskleber import Receiver


class MockReceiver(Receiver):
    def __init__(self) -> None:
        self.n_called = 0

    async def receive(self) -> tuple[bool, dict[str, Any]]:
        self.n_called += 1
        return True, {"msg": "Called MockReceiver", "count": self.n_called}

    async def start(self) -> None:
        return

    async def stop(self) -> None:
        return

    def __repr__(self) -> str:
        return "MockReceiver"


@pytest.mark.asyncio
async def test_mock_receiver_can_be_iterated_over() -> None:
    count = 1

    async for data, meta in MockReceiver():
        assert data
        assert "msg" in meta
        assert meta["count"] == count
        count += 1
        if count == 3:
            break


@pytest.mark.asyncio
async def test_mock_receiver_call_anext() -> None:
    receiver = MockReceiver()

    data, meta = await anext(receiver)

    assert data
    assert meta["count"] == 1

    data, meta = await anext(receiver)

    assert meta["count"] == 2
