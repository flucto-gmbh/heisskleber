import socket
import warnings
from dataclasses import dataclass


@dataclass
class BaseConf:
    """
    default configuration class for generic configuration info
    """

    verbose: bool = False
    print_stdout: bool = False

    def __setitem__(self, key, value):
        if hasattr(self, key):
            self.__setattr__(key, value)
        else:
            warnings.warn(UserWarning(f"no such class member: {key}"), stacklevel=2)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            warnings.warn(UserWarning(f"no such class member: {key}"), stacklevel=2)

    @property
    def serial_number(self):
        return socket.gethostname().upper()
