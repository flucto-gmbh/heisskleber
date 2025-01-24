from heisskleber.core import register

from .config import FileConf
from .receiver import FileReader
from .sender import FileWriter

register("file", FileWriter, FileReader, FileConf)

__all__ = ["FileConf", "FileReader", "FileWriter"]
