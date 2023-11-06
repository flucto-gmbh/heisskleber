import json
import pickle
from typing import Any

import pytest

from heisskleber.core.packer import get_packer, get_unpacker, serialpacker


def test_get_packer() -> None:
    assert get_packer("json") == json.dumps
    assert get_packer("pickle") == pickle.dumps
    assert get_packer("default") == json.dumps
    assert get_packer("foobar") == json.dumps
    assert get_packer("serial") == serialpacker


def test_get_unpacker() -> None:
    assert get_unpacker("json") == json.loads
    assert get_unpacker("pickle") == pickle.loads
    assert get_unpacker("default") == json.loads
    assert get_unpacker("foobar") == json.loads


@pytest.mark.parametrize(
    "message,expected",
    [
        ({"hi": 1, "da": 2, "nei": 3}, "1,2,3"),
        ({"er": 1, "ma": "ga", "gerd": 3, "jo": 4}, "1,ga,3,4"),
        ({"": 1, "ho": 0.0, "lee": 0.1, "shit": 1_000}, "1,0.0,0.1,1000"),
        ({"be": 1e6, "li": 1_000}, "1000000.0,1000"),
    ],
)
def test_serial_packer_functionality(message: dict[str, Any], expected: str) -> None:
    assert serialpacker(message) == expected
