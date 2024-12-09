import json
from dataclasses import dataclass
from typing import Any

import pytest

from heisskleber.core import Packer, json_packer
from heisskleber.core.packer import PackerError


@pytest.fixture
def packer() -> Packer[dict[str, Any]]:
    return json_packer


def test_simple_dict(packer: Packer[dict[str, Any]]) -> None:
    """Test packing a simple dictionary"""
    test_data = {"key": "value"}
    result = packer(test_data)
    assert result == b'{"key": "value"}'
    # Verify it can be decoded back
    assert json.loads(result.decode()) == test_data


def test_nested_dict(packer: Packer[dict[str, Any]]) -> None:
    """Test packing a nested dictionary"""
    test_data = {"string": "value", "number": 42, "nested": {"bool": True, "list": [1, 2, 3]}}
    result = packer(test_data)
    # Verify it can be decoded back to the same structure
    assert json.loads(result.decode()) == test_data


def test_empty_dict(packer: Packer[dict[str, Any]]) -> None:
    """Test packing an empty dictionary"""
    test_data = {}
    result = packer(test_data)
    assert result == b"{}"


def test_special_characters(packer: Packer[dict[str, Any]]) -> None:
    """Test packing data with special characters"""
    test_data = {"special": "Hello\nWorld\t!", "unicode": "🌍🌎🌏"}
    result = packer(test_data)
    # Verify it can be decoded back
    assert json.loads(result.decode()) == test_data


def test_non_serializable_values(packer: Packer[dict[str, Any]]) -> None:
    """Test that non-JSON-serializable values raise TypeError"""

    @dataclass
    class NonSerializable:
        x: int

    test_data = {"key": NonSerializable(42)}
    with pytest.raises(PackerError):
        packer(test_data)


def test_large_dict(packer: Packer[dict[str, Any]]) -> None:
    """Test packing a large dictionary"""
    test_data = {str(i): f"value_{i}" for i in range(1000)}
    result = packer(test_data)
    # Verify it can be decoded back
    assert json.loads(result.decode()) == test_data
