"""Packer and unpacker for network data."""
import json
import pickle
from typing import Any, Callable

from .types import Serializable


def get_packer(style: str) -> Callable[[dict[str, Serializable]], str]:
    """Return a packer function for the given style.

    Packer func serializes a given dict."""
    if style in _packstyles:
        return _packstyles[style]
    else:
        return _packstyles["default"]


def get_unpacker(style: str) -> Callable[[str], dict[str, Serializable]]:
    """Return an unpacker function for the given style.

    Unpacker func deserializes a string."""
    if style in _unpackstyles:
        return _unpackstyles[style]
    else:
        return _unpackstyles["default"]


def serialpacker(data: dict[str, Any]) -> str:
    return ",".join([str(v) for v in data.values()])


_packstyles: dict[str, Callable[[dict[str, Serializable]], str]] = {
    "default": json.dumps,
    "json": json.dumps,
    "pickle": pickle.dumps,  # type: ignore
    "serial": serialpacker,
}

_unpackstyles: dict[str, Callable[[str], dict[str, Serializable]]] = {
    "default": json.loads,
    "json": json.loads,
    "pickle": pickle.loads,  # type: ignore
}
