import json
from collections.abc import Callable
from dataclasses import dataclass, fields
from datetime import timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

from heisskleber.core import BaseConf
from heisskleber.core.packer import PackerError


class CSVPacker:
    """Helper class to write csv files."""

    def __init__(self) -> None:
        self.fields: list[str] = []

    def packer(self, data: dict[str, Any]) -> str:
        """Create a string of ordered fields from dictionary values."""
        return ",".join([str(data.get(field, "")) for field in self.fields])

    def header(self, data: dict[str, Any]) -> list[str]:
        """Create header for csv field."""
        self.fields = list(data.keys())
        return [
            "sep=,",
            "#encoding=UTF-8",
            "#datatype:" + ",".join(type(v).__name__ for v in data.values()),
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
