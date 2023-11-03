"""Packer and unpacker for network data."""
import json
import pickle
from typing import Callable


def get_packer(style) -> Callable[[dict], str]:
    """Return a packer function for the given style.

    Packer func serializes a given dict."""
    if style in _packstyles:
        return _packstyles[style]
    else:
        return _packstyles["default"]


def get_unpacker(style) -> Callable[[str], dict]:
    """Return an unpacker function for the given style.

    Unpacker func deserializes a string."""
    if style in _unpackstyles:
        return _unpackstyles[style]
    else:
        return _unpackstyles["default"]


def serialpacker(data: dict) -> str:
    return ",".join([str(v) for v in data.values()])


_packstyles = {
    "default": json.dumps,
    "json": json.dumps,
    "pickle": pickle.dumps,
    "serial": serialpacker,
    "raw": lambda x: x,
}

_unpackstyles = {
    "default": json.loads,
    "json": json.loads,
    "pickle": pickle.loads,
    "raw": lambda x: x,
}
