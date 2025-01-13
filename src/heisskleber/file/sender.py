import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

import aiofiles
import aiofiles.threadpool

from heisskleber.core import Packer, Sender, json_packer
from heisskleber.file.config import FileConf

T = TypeVar("T")


class FileWriter(Sender[T]):
    """Asynchronous file writer implementation of the Sender interface.

    Writes data to files with automatic rollover based on time intervals.
    Files are named according to the configured datetime format.
    """

    def __init__(self, base_path: Path | str, config: FileConf, packer: Packer[T] = json_packer) -> None:
        """Initialize the file writer.

        Args:
            base_path: Directory path where files will be written
            config: Configuration for file rollover and naming
            packer: Optional packer for serializing data
        """
        self.base_path = Path(base_path)
        self.config = config
        self.packer = packer

        self._current_file = aiofiles.open("test.txt")
        self._rollover_task: asyncio.Task | None = None
        self._last_rollover: float = 0

    def _get_filename(self) -> Path:
        """Generate filename based on current timestamp."""
        return self.base_path / datetime.now().strftime(self.config.name_fmt)

    async def _rollover(self) -> None:
        """Close current file and open a new one."""
        if self._current_file is not None:
            await self._current_file.close()

        filename = self._get_filename()
        filename.parent.mkdir(parents=True, exist_ok=True)
        self._current_file = await aiofiles.open(filename, mode="a")
        self._last_rollover = asyncio.get_event_loop().time()
        logging.info(f"Rolled over to new file: {filename}")

    async def _rollover_loop(self) -> None:
        """Background task that handles periodic file rollover."""
        while True:
            try:
                now = asyncio.get_event_loop().time()
                if now - self._last_rollover >= self.config.rollover:
                    await self._rollover()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in rollover loop: {e}")
                await asyncio.sleep(1)  # Avoid tight loop on error

    async def send(self, data: str, **kwargs: Any) -> None:
        """Write data to the current file.

        Args:
            data: String data to write
            **kwargs: Additional arguments (unused)

        Raises:
            RuntimeError: If writer hasn't been started
        """
        if self._current_file is None:
            raise RuntimeError("FileWriter not started")

        packed_data = self.packer.pack(data)
        await self._current_file.write(packed_data + "\n")
        await self._current_file.flush()

    async def start(self) -> None:
        """Start the file writer and rollover background task."""
        await self._rollover()  # Open initial file
        self._rollover_task = asyncio.create_task(self._rollover_loop())

    async def stop(self) -> None:
        """Stop the writer and cleanup resources."""
        if self._rollover_task:
            self._rollover_task.cancel()
            try:
                await self._rollover_task
            except asyncio.CancelledError:
                pass

        if self._current_file:
            await self._current_file.close()
            self._current_file = None

    def __repr__(self) -> str:
        status = "started" if self._current_file else "stopped"
        return f"AsyncFileWriter(path='{self.base_path}', status={status})"
