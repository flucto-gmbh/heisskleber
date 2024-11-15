"""Core classes of the heisskleber library."""

from .config import BaseConf, ConfigType
from .packer import JSONPacker, Packer, PackerError, T_contra
from .sink import AsyncSink, T
from .source import AsyncSource
from .unpacker import JSONUnpacker, T_co, Unpacker, UnpackError

json_packer = JSONPacker()
json_unpacker = JSONUnpacker()

__all__ = [
    "Packer",
    "Unpacker",
    "AsyncSink",
    "AsyncSource",
    "json_packer",
    "json_unpacker",
    "BaseConf",
    "ConfigType",
    "T",
    "T_co",
    "T_contra",
    "PackerError",
    "UnpackError",
]
