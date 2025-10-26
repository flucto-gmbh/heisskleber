from dataclasses import dataclass
from enum import StrEnum

from heisskleber.core import BaseConf

__all__ = ["HTTPConf"]


@dataclass
class HTTPConf(BaseConf):
    """Configuration dataclass for HTTP connections."""

    class Proto(StrEnum):  # noqa: D106
        HTTP = "http"
        HTTPS = "https"

    host: str = "localhost"
    port: int = 8080
    protocol: Proto = Proto.HTTP
    url_path: str = "/"
    max_buffer_size: int = 100
