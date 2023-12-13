import asyncio
from typing import Optional


class CsvUnpacker:
    header: Optional[list[str]] = None

    def __call__(self, payload: str) -> dict:
        if not self.header:
            self.header = payload.split(",")
            return {}

        return dict(zip(self.header, payload.split(",")))


class AsyncFileSource:
    def __init__(self, path):
        self._path = path
        self._line: Optional[str] = None
        self._read_event = asyncio.Event()
        self._receive_event = asyncio.Event()
        self._reader_task: Optional[asyncio.Task] = None
        self._unpacker = CsvUnpacker()

    async def read_file(self):
        with open(self._path) as f:
            while True:
                # wait for the next read to be requested
                await self._read_event.wait()
                self._read_event.clear()

                # read line
                self._line = f.readline().strip()

                # Handle the end of the file
                if self._line == "":
                    self._line = None
                    break

                # okay, I've read a line, time for the receive function
                self._receive_event.set()

    async def receive(self) -> dict:
        # Schedule the reader
        if self._reader_task is None:
            self._reader_task = asyncio.create_task(self.read_file())

        # signal the reader to start
        self._read_event.set()

        # wait for the next line to be read
        await self._receive_event.wait()
        self._receive_event.clear()

        return self._unpacker(self._line)
