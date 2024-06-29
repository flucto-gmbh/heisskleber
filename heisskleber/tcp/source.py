"""
Async TCP Source - get data from arbitrary TCP server
"""

import asyncio
import logging
from typing import Callable

from heisskleber.core.types import AsyncSource, Serializable
from heisskleber.tcp.config import TcpConf


def bytes_csv_unpacker(data: bytes) -> tuple[str, dict[str, str]]:
    vals = data.decode().rstrip().split(",")
    keys = [f"key{i}" for i in range(len(vals))]
    return ("tcp", dict(zip(keys, vals)))


class AsyncTcpSource(AsyncSource):
    """
    Async TCP connection, connects to host:port and reads byte encoded strings.


    Pass an unpack function like so:

    Example
    -------
    def unpack(data: bytes) -> tuple[str, dict[str, float | int | str]]:
        return dict(zip(["key1", "key2"], data.decode().split(","))

    """

    def __init__(self, config: TcpConf, unpack: Callable[[bytes], tuple[str, dict[str, Serializable]]] | None) -> None:
        self.logger = logging.getLogger("AsyncTcpSource")
        self.config = config
        self.is_connected = False
        self.unpack = unpack or bytes_csv_unpacker
        self.timeout = config.timeout
        self._start_task: asyncio.Task[None] | None = None

    async def receive(self) -> tuple[str, dict[str, Serializable]]:
        data = b""
        retry_delay = self.config.retry_delay
        while not data:
            await self._ensure_connected()
            data = await self.reader.readline()
            if not data:
                self.is_connected = False
                self.logger.warning(f"{self} nothing received, retrying connect in {retry_delay}s")
                await asyncio.sleep(retry_delay)
                retry_delay = min(self.config.timeout, retry_delay * 2)

        topic, payload = self.unpack(data)
        return topic, payload  # type: ignore

    def start(self) -> None:
        self._start_task = asyncio.create_task(self._connect())

    async def start_async(self) -> None:
        await self._ensure_connected()

    def stop(self) -> None:
        if self.is_connected:
            self.logger.info(f"{self} stopping")

    async def _ensure_connected(self) -> None:
        if self.is_connected:
            return

        # Not connected, try to (re-)connect
        if not self._start_task:
            self.start()

        try:
            await self._start_task
        finally:
            self._start_task = None

    async def _connect(self) -> None:
        self.logger.info(f"{self} waiting for connection.")

        num_attempts = 0
        while True:
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.config.host, self.config.port),
                    timeout=self.timeout)
                self.logger.info(f"{self} connected successfully!")
                break
            except (ConnectionRefusedError, asyncio.TimeoutError) as e:
                self.logger.exception(f'{self}: {type(e).__name__}')
                if self.config.restart_behavior == TcpConf.RestartBehavior.NEVER:
                    raise
                num_attempts += 1
                if self.config.restart_behavior == TcpConf.RestartBehavior.ONCE and num_attempts > 1:
                    raise
                # otherwise retry indefinitely

        self.is_connected = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
