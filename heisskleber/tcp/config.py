from dataclasses import dataclass
from enum import Enum

from heisskleber.core import BaseConf


@dataclass
class TcpConf(BaseConf):
    """Configuration dataclass for TCP connections."""

    class RestartBehavior(Enum):
        """The three types of restart behaviour."""

        NEVER = 0  # Never restart on failure
        ONCE = 1  # Restart once
        ALWAYS = 2  # Restart until the connection succeeds

    host: str = "localhost"
    port: int = 6000
    timeout: int = 60
    retry_delay: float = 0.5
    restart_behavior: RestartBehavior = RestartBehavior.ALWAYS
