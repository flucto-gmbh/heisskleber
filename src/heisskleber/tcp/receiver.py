"""Async TCP Source - get data from arbitrary TCP server."""

import asyncio
import logging
from typing import Any, TypeVar

from heisskleber.core import Receiver, Unpacker, json_unpacker
from heisskleber.tcp.config import TcpConf

T = TypeVar("T")

logger = logging.getLogger("heisskleber.tcp")


class TcpReceiver(Receiver[T]):
    """Async TCP connection, connects to host:port and reads byte encoded strings."""

    def __init__(self, config: TcpConf, unpacker: Unpacker[T] = json_unpacker) -> None:  # type: ignore [assignment]
        self.config = config
        self.unpack = unpacker
        self.is_connected = False
        self.timeout = config.timeout
        self._start_task: asyncio.Task[None] | None = None
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    async def receive(self) -> tuple[T, dict[str, Any]]:
        """Receive data from a connection.

        Attempt to read data from the connection and handle the process of re-establishing the connection if necessary.

        Returns:
            tuple[T, dict[str, Any]]
                - The unpacked message data
                - A dictionary with metadata including the message topic

        Raises:
            TypeError: If the message payload is not of type bytes.
            UnpackerError: If the message could not be unpacked with the unpacker protocol.

        """
        data = b""
        retry_delay = self.config.retry_delay
        while not data:
            await self._ensure_connected()
            data = await self.reader.readline()  # type: ignore [union-attr]
            if not data:
                self.is_connected = False
                logger.warning(
                    "%(self)s nothing received, retrying connect in %(seconds)s",
                    {"self": self, "seconds": retry_delay},
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(self.config.timeout, retry_delay * 2)

        payload, extra = self.unpack(data)
        return payload, extra

    async def start(self) -> None:
        """Start TcpSource."""
        await self._connect()

    async def stop(self) -> None:
        """Stop TcpSource."""
        if self.is_connected:
            logger.info("%(self)s stopping", {"self": self})

    async def _ensure_connected(self) -> None:
        if self.is_connected:
            return

        # Not connected, try to (re-)connect
        if not self._start_task:
            # Possibly multiple reconnects, so can't just await once
            self._start_task = asyncio.create_task(self._connect())

        try:
            await self._start_task
        finally:
            self._start_task = None

    async def _connect(self) -> None:
        logger.info("%(self)s waiting for connection.", {"self": self})

        num_attempts = 0
        while True:
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.config.host, self.config.port),
                    timeout=self.timeout,
                )
                logger.info("%(self)s connected successfully!", {"self": self})
                break
            except ConnectionRefusedError as e:
                logger.exception("%(self)s: %(error_type)s", {"self": self, "error_type": type(e).__name__})
                if self.config.restart_behavior == TcpConf.RestartBehavior.NEVER:
                    raise
                num_attempts += 1
                if self.config.restart_behavior == TcpConf.RestartBehavior.ONCE and num_attempts > 1:
                    raise
                # otherwise retry indefinitely

        self.is_connected = True

    def __repr__(self) -> str:
        """Return string representation of TcpSource."""
        return f"{self.__class__.__name__}(host={self.config.host}, port={self.config.port})"
