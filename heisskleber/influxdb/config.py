from dataclasses import dataclass

from heisskleber.config import BaseConf


@dataclass
class InfluxDBConf(BaseConf):
    host: str = "localhost"
    port: int = 8086
    bucket: str = "test"
    org: str = "test"
    ssl: bool = False
    read_token: str = ""
    write_token: str = ""
    all_access_token: str = ""

    @property
    def url(self) -> str:
        protocol = "https" if self.ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"
