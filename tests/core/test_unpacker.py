from dataclasses import dataclass
from typing import Any

from heisskleber.core import Unpacker, json_unpacker


@dataclass
class HotGlue:
    name: str
    weight: float


class DataclassUnpacker(Unpacker[HotGlue]):
    """Take a csv of 'name,weight' and construct a HotGlue dataclass.

    Raises:
        TypeError: The csv was not formatted properly or a dataclass could not be constructed.

    """

    def __call__(self, payload: bytes) -> tuple[HotGlue, dict[str, Any]]:
        extra = {"type": "custom"}
        try:
            name, weight = payload.decode().split(",")
            return HotGlue(name, float(weight)), extra
        except UnicodeDecodeError as e:
            raise TypeError from e


def test_custom_unpacker() -> None:
    unpacker = DataclassUnpacker()

    data, extra = unpacker(b"hotglue,10.0")
    assert isinstance(data, HotGlue)
    assert data == HotGlue("hotglue", 10.0)

    assert extra == {"type": "custom"}


def test_simple_bytestring() -> None:
    """Test packing a simple dictionary"""

    test_data = b'{"key": "value"}'
    data, extra = json_unpacker(test_data)
    assert data == {"key": "value"}
    assert extra == {}


def test_nested_dict() -> None:
    """Test packing a nested dictionary"""
    test_data = b'{"string": "value", "number": 42, "nested": {"bool": true, "list": [1, 2, 3]}}'
    data, extra = json_unpacker(test_data)

    assert data == {"string": "value", "number": 42, "nested": {"bool": True, "list": [1, 2, 3]}}
    assert extra == {}
