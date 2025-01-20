from dataclasses import dataclass, fields
from datetime import timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

from heisskleber.core import BaseConf


@dataclass
class FileConf(BaseConf):
    """Config class for file operations."""

    rollover: int = 3600
    name_fmt: str = "%Y%m%d_%h%M%s.txt"
    directory: str = "./"
    watchfile: str = ""
    tz: tzinfo = timezone.utc

    @classmethod
    def from_dict(cls: type["FileConf"], config_dict: dict[str, Any]) -> "FileConf":
        """Create FileConf from dictionary."""
        valid_fields = {f.name for f in fields(cls)}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        filtered_dict["tz"] = ZoneInfo(filtered_dict["tzt"])  # the override
        return cls(**filtered_dict)
