from heisskleber.core import register

from .config import ZmqConf
from .receiver import ZmqReceiver
from .sender import ZmqSender

register("zmq", ZmqSender, ZmqReceiver, ZmqConf)

__all__ = ["ZmqConf", "ZmqReceiver", "ZmqSender"]
