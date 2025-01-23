from heisskleber.core import register

from .config import ConsoleConf
from .receiver import ConsoleReceiver
from .sender import ConsoleSender

register("console", ConsoleSender, ConsoleReceiver, ConsoleConf)

__all__ = ["ConsoleReceiver", "ConsoleSender"]
