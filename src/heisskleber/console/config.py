from dataclasses import dataclass

from heisskleber.core.config import BaseConf


@dataclass
class ConsoleConf(BaseConf):
    """Configuration class for Console operations."""

    verbose: bool = False
    pretty: bool = False
