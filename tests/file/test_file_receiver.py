import asyncio
from pathlib import Path
from typing import Any

import pytest

from heisskleber.file import FileConf, FileReader


def str_unpacker(payload: bytes) -> tuple[str, dict[str, Any]]:
    return payload.decode(), {}


async def write_in(file, text, delay) -> None:
    await asyncio.sleep(delay)
    with file.open("ba") as f:
        f.write(text)


@pytest.mark.asyncio
async def test_file_receiver(tmp_path: Path) -> None:
    file = tmp_path / "testfile"

    config = FileConf(watchfile=str(file))
    receiver = FileReader(config, unpacker=str_unpacker)

    with file.open("bw") as f:
        f.write(b"First line\n")

    future = asyncio.create_task(write_in(file, b"text", 0.1))
    data, extra = await asyncio.wait_for(receiver.receive(), 1.0)
    await future
    assert data == "text"

    future = asyncio.create_task(write_in(file, b"more text", 0.1))
    data, extra = await asyncio.wait_for(receiver.receive(), 1.0)
    assert data == "more text"
    await future
