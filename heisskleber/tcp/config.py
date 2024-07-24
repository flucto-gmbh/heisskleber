from dataclasses import dataclass
from enum import Enum

from heisskleber.config import BaseConf


@dataclass
class TcpConf(BaseConf):
    class RestartBehavior(Enum):
        NEVER = 0  # Never restart on failure
        ONCE = 1  # Restart once
        INFINITELY = 2  # Restart until the connection succeeds

    host: str = "localhost"
    port: int = 6000
    timeout: int = 60
    retry_delay: float = 0.5
    restart_behavior: RestartBehavior = RestartBehavior.INFINITELY
