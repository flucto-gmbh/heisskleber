from heisskleber.core import register

from .config import TcpConf
from .receiver import TcpReceiver
from .sender import TcpSender

register("tcp", TcpSender, TcpReceiver, TcpConf)

__all__ = ["TcpConf", "TcpReceiver", "TcpSender"]
