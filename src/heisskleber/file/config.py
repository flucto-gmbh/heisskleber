from dataclasses import dataclass

from heisskleber.core import BaseConf


@dataclass
class FileConf(BaseConf):
    """Config class for file operations."""

    rollover: int = 3600
    name_fmt: str = "%Y%m%d_%h%M%s.txt"
    directory: str = "./"
