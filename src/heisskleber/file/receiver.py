import asyncio
import logging
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
from io import BufferedReader
from pathlib import Path
from typing import Any, TypeVar

from watchfiles import Change, awatch

from heisskleber.core import Receiver, Unpacker
from heisskleber.file.config import FileConf

T = TypeVar("T")
logger = logging.getLogger("heisskleber.mqtt")


class FileReader(Receiver[T]):
    """Asynchronous File Reader.

    Currently only reads bytes.
    """

    def __init__(
        self,
        config: FileConf,
        unpacker: Unpacker[T],
    ) -> None:
        self.config = config
        self.unpacker = unpacker
        self._stop_event = asyncio.Event()
        self._iter = self._fileiter()
        self._loop = asyncio.get_running_loop()
        self._executor = ThreadPoolExecutor()
        self._current_file: BufferedReader | None = None

    async def _fileiter(self) -> AsyncGenerator[tuple[T, dict[str, Any]]]:
        """Iterator function to parse changes in watched files.

        Main mode of operation is to watch for added content in a file.
        """
        filesizes: dict[str, int] = {}  # currently only supports watching a single file
        filesizes[self.config.watchfile] = Path(self.config.watchfile).stat().st_size  # get status quo of file

        async for changes in awatch(self.config.watchfile, stop_event=self._stop_event):
            for changetype, filepath in changes:
                if changetype not in (Change.added, Change.modified):
                    continue
                path = Path(filepath)
                current_size = path.stat().st_size
                previous_size = filesizes.get(filepath, 0)

                if current_size > previous_size:
                    content = await self._async_read(path, previous_size)
                    data, extra = self.unpacker(content)
                    extra.update({"filepath": filepath, "timestamp": asyncio.get_running_loop().time()})
                    yield (data, extra)

                filesizes[filepath] = current_size

    async def _async_read(self, path: Path, start: int = 0) -> bytes:
        if self._current_file is None:
            self._current_file = await self._open_file(path)
        await self._loop.run_in_executor(self._executor, self._current_file.seek, start)
        return await self._loop.run_in_executor(self._executor, self._current_file.read)

    async def _open_file(self, filename: Path) -> BufferedReader:
        """Open file asynchronously."""
        return await self._loop.run_in_executor(self._executor, lambda: filename.open(mode="rb"))

    async def _close_file(self) -> None:
        if self._current_file is not None:
            await self._loop.run_in_executor(self._executor, self._current_file.close)

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Get the next data and extra tuple from the watched file."""
        return await anext(self._iter)

    def __repr__(self) -> str:
        """Return string representation of Mqtt Source class."""
        return f"{self.__class__.__name__}()"

    async def start(self) -> None:
        """Open the file reader listener task."""

    async def stop(self) -> None:
        """Stop the file reader."""
        self._stop_event.set()
