import asyncio
import contextlib
import json
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Any, TypeVar

from heisskleber.core import Packer, PackerError, Sender
from heisskleber.file.config import FileConf

T = TypeVar("T")

logger = logging.getLogger("heisskleber.file")


def json_packer(data: dict[str, Any]) -> str:
    """Pack to json string."""
    try:
        return json.dumps(data)
    except json.JSONDecodeError:
        raise PackerError(data) from None


def csv_packer(data: dict[str, Any]) -> str:
    """Create csv string from data."""
    return ",".join(map(str, data.values()))


class FileWriter(Sender[T]):
    """Asynchronous file writer implementation of the Sender interface.

    Writes data to files with automatic rollover based on time intervals.
    Files are named according to the configured datetime format.
    """

    def __init__(
        self,
        config: FileConf,
        packer: Packer[T] = json_packer,  # type: ignore[assignment]
        header_func: Callable[[T], list[str]] | None = None,
    ) -> None:
        """Initialize the file writer.

        Args:
            config: Configuration for file rollover and naming
            header_func: Function to extract header from T
            packer: Optional packer for serializing data
        """
        self.base_path = Path(config.directory)
        self.config = config
        self.header_func = header_func
        self.packer = packer

        self._executor = ThreadPoolExecutor(max_workers=1)
        self._loop = asyncio.get_running_loop()
        self._header: list[str] | None = None

        self._current_file: TextIOWrapper | None = None
        self._rollover_task: asyncio.Task[None] | None = None
        self._last_rollover: float = 0
        self.filename: Path = Path()

    async def _open_file(self, filename: Path) -> TextIOWrapper:
        """Open file asynchronously."""
        return await self._loop.run_in_executor(self._executor, lambda: filename.open(mode="a"))

    async def _close_file(self) -> None:
        if self._current_file is not None:
            await self._loop.run_in_executor(self._executor, self._current_file.close)

    async def _write_header(self) -> None:
        if not self._header or not self._current_file:
            return
        for line in self._header:
            await self._loop.run_in_executor(self._executor, self._current_file.write, line)
            await self._loop.run_in_executor(self._executor, self._current_file.write, "\n")

    async def _rollover(self) -> None:
        """Close current file and open a new one."""
        if self._current_file is not None:
            await self._close_file()

        self.filename = self.base_path / datetime.now(self.config.tz).strftime(self.config.name_fmt)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self._current_file = await self._open_file(self.filename)
        self._last_rollover = self._loop.time()
        logger.info("Rolled over to new file: %s", self.filename)
        await self._write_header()

    async def _rollover_loop(self) -> None:
        """Background task that handles periodic file rollover."""
        while True:
            now = self._loop.time()
            if now - self._last_rollover >= self.config.rollover:
                await self._rollover()
            await asyncio.sleep(1)

    async def send(self, data: T, **kwargs: Any) -> None:
        """Write data to the current file.

        Args:
            data: Data to write
            **kwargs: Additional arguments (unused)

        Raises:
            RuntimeError: If writer hasn't been started
        """
        if not self._rollover_task:
            await self.start()
        if not self._current_file:
            raise RuntimeError("FileWriter not started")
        if not self._header and self.header_func is not None:
            self._header = self.header_func(data)
            await self._write_header()

        payload = self.packer(data)
        if isinstance(payload, bytes | bytearray):
            payload = payload.decode()
        await self._loop.run_in_executor(self._executor, self._current_file.write, payload)
        await self._loop.run_in_executor(self._executor, self._current_file.write, "\n")

    async def start(self) -> None:
        """Start the file writer and rollover background task."""
        await self._rollover()  # Open initial file
        self._rollover_task = asyncio.create_task(self._rollover_loop())

    async def stop(self) -> None:
        """Stop the writer and cleanup resources."""
        if self._rollover_task:
            self._rollover_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._rollover_task
            self._rollover_task = None

        if self._current_file:
            await self._close_file()
            self._current_file = None

    def __repr__(self) -> str:
        """Return string representation of FileWriter."""
        status = "started" if self._current_file else "stopped"
        return f"FileWriter(path='{self.base_path}', status={status})"
