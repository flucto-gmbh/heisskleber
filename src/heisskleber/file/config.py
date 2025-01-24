import json
from collections.abc import Callable
from dataclasses import dataclass, fields
from datetime import timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

from heisskleber.core import BaseConf
from heisskleber.core.packer import PackerError


def flatten_dict(dict_in: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """Return a flattened dict from a nested dict.

    Example:
      >>> dict_in = {"pos": {"x": 1, "y": 2}}
      >>> flatten_dict(dict_in, sep=".")
      {'pos.x': 1, 'pos.y': 2}

    """
    dict_out = {}
    for key, value in dict_in.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            dict_out.update(flatten_dict(value, new_key, sep=sep))
        else:
            dict_out[new_key] = value
    return dict_out


class CSVPacker:
    """Helper class to write csv files."""

    def __init__(self) -> None:
        self.fields: list[str] = []

    def packer(self, data: dict[str, Any]) -> str:
        """Create a string of ordered fields from dictionary values."""
        flat_dict = flatten_dict(data)
        return ",".join([str(flat_dict.get(field, "")) for field in self.fields])

    def header(self, data: dict[str, Any]) -> list[str]:
        """Create header for csv field."""
        flat_dict = flatten_dict(data)
        self.fields = list(flat_dict.keys())
        return [
            ",".join(self.fields),
        ]


def json_packer(data: dict[str, Any]) -> str:
    """Pack dictionary into json string."""
    try:
        return json.dumps(data)
    except (TypeError, UnicodeDecodeError) as err:
        raise PackerError(data) from err


@dataclass
class FileConf(BaseConf):
    """Config class for file operations."""

    rollover: int = 3600
    name_fmt: str = "%Y%m%d_%h%M%s.txt"
    directory: str = "./"
    watchfile: str = ""
    format: str = "json"
    tz: tzinfo = timezone.utc

    def __post_init__(self) -> None:
        """Add csv helper class."""
        if self.format not in ["csv", "json", "user", None]:
            raise TypeError("Format not supported, choosen one of csv, json, user, none.")
        self._csv = CSVPacker()
        return super().__post_init__()

    @property
    def packer(self) -> Callable[[dict[str, Any]], str] | None:
        """Return packer based on format."""
        if self.format == "json":
            return json_packer
        if self.format == "csv":
            return self._csv.packer
        return None

    @property
    def header(self) -> Callable[[dict[str, Any]], list[str]] | None:
        """Return header func based on format."""
        if self.format == "csv":
            return self._csv.header
        return None

    @classmethod
    def from_dict(cls: type["FileConf"], config_dict: dict[str, Any]) -> "FileConf":
        """Create FileConf from dictionary."""
        valid_fields = {f.name for f in fields(cls)}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        filtered_dict["tz"] = ZoneInfo(filtered_dict.get("tz", "UTC"))
        return cls(**filtered_dict)
