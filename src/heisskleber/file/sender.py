import asyncio
import contextlib
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BufferedWriter
from pathlib import Path
from typing import Any, TypeVar

from heisskleber.core import Packer, Sender, json_packer
from heisskleber.file.config import FileConf

T = TypeVar("T")

logger = logging.getLogger("heisskleber.file")


class FileWriter(Sender[T]):
    """Asynchronous file writer implementation of the Sender interface.

    Writes data to files with automatic rollover based on time intervals.
    Files are named according to the configured datetime format.
    """

    def __init__(self, config: FileConf, packer: Packer[T] = json_packer) -> None:  # type: ignore[assignment]
        """Initialize the file writer.

        Args:
            base_path: Directory path where files will be written
            config: Configuration for file rollover and naming
            packer: Optional packer for serializing data
        """
        self.base_path = Path(config.directory)
        self.config = config
        self.packer = packer

        self._executor = ThreadPoolExecutor(max_workers=1)
        self._loop = asyncio.get_running_loop()

        self._current_file: BufferedWriter | None = None
        self._rollover_task: asyncio.Task | None = None
        self._last_rollover: float = 0
        self.filename: Path = Path()

    async def _open_file(self, filename: Path) -> BufferedWriter:
        """Open file asynchronously."""
        return await self._loop.run_in_executor(self._executor, lambda: filename.open(mode="ab"))

    async def _close_file(self) -> None:
        if self._current_file is not None:
            await self._loop.run_in_executor(self._executor, self._current_file.close)

    async def _rollover(self) -> None:
        """Close current file and open a new one."""
        if self._current_file is not None:
            await self._close_file()

        self.filename = self.base_path / datetime.now(self.config.tz).strftime(self.config.name_fmt)
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self._current_file = await self._open_file(self.filename)
        self._last_rollover = self._loop.time()
        logger.info("Rolled over to new file: %s", self.filename)

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

        payload = self.packer(data)
        await self._loop.run_in_executor(self._executor, self._current_file.write, payload)
        await self._loop.run_in_executor(self._executor, self._current_file.write, b"\n")

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
