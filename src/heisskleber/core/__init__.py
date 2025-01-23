"""Core classes of the heisskleber library."""

from typing import Any

from .config import BaseConf, ConfigType
from .packer import JSONPacker, Packer, PackerError
from .receiver import Receiver
from .sender import Sender
from .unpacker import JSONUnpacker, Unpacker, UnpackerError

json_packer = JSONPacker()
json_unpacker = JSONUnpacker()


_sender_registry: dict[str, type[Sender[Any]]] = {}
_receiver_registry: dict[str, type[Receiver[Any]]] = {}
_config_registry: dict[str, type[BaseConf]] = {}


def register(name: str, sender: type[Sender[Any]], receiver: type[Receiver[Any]], config: type[BaseConf]) -> None:
    """Register classes."""
    _sender_registry[name] = sender
    _receiver_registry[name] = receiver
    _config_registry[name] = config


__all__ = [
    "BaseConf",
    "ConfigType",
    "Packer",
    "PackerError",
    "Receiver",
    "Sender",
    "Unpacker",
    "UnpackerError",
    "json_packer",
    "json_unpacker",
    "register",
]
