from heisskleber.core import register

from .config import UdpConf
from .receiver import UdpReceiver
from .sender import UdpSender

register("udp", UdpSender, UdpReceiver, UdpConf)

__all__ = ["UdpConf", "UdpReceiver", "UdpSender"]
