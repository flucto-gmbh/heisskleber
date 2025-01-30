import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from freezegun import freeze_time

from heisskleber.file import FileConf, FileWriter


@pytest.fixture
def config() -> FileConf:
    return FileConf(
        rollover=3600,  # 1 hour rollover
        name_fmt="%Y%m%d_%H.txt",
    )


@pytest.mark.asyncio
async def test_file_writer_basic_operations(config: FileConf) -> None:
    """Test basic file operations: open, write, close."""
    writer = FileWriter(config)

    # Test starting the writer
    await writer.start()
    assert writer._current_file is not None
    assert writer._background_task is not None

    # Test writing data
    test_data = {"message": "hello world"}
    await writer.send(test_data)

    # Test file content
    current_file = writer.filename
    assert current_file.exists()

    await writer.stop()
    assert writer._current_file is None
    assert writer._background_task is None

    # Verify file content after closing
    content = current_file.read_text().split("\n")[0]
    assert content == json.dumps(test_data)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_file_writer_rollover(tmp_path: Path) -> None:
    """Test file rollover functionality."""
    config = FileConf(rollover=2, name_fmt="%Y%m%d_%H%M%s.txt", directory=str(tmp_path))  # 2 second rollover
    writer: FileWriter[dict[str, Any]] = FileWriter(config)

    with freeze_time("2024-01-01 12:00:00") as frozen_time:
        await writer.start()
        first_file = writer.filename
        await writer.send({"message": "first file"})

        # Move time forward past rollover period
        frozen_time.tick(delta=3)  # advance 3 seconds

        await writer.send({"message": "second file"})
        second_file = writer.filename

        await writer.stop()

        assert first_file != second_file
        assert first_file.exists()
        assert second_file.exists()
        assert "first file" in first_file.read_text()


@pytest.mark.asyncio
async def test_file_writer_rollover_natural(tmp_path: Path) -> None:
    """Test file rollover functionality."""
    config = FileConf(rollover=2, name_fmt="%Y%m%d_%H%M%s.txt", directory=str(tmp_path))  # 2 second rollover
    writer: FileWriter[dict[str, Any]] = FileWriter(config)

    await writer.start()

    assert writer._background_task is not None
    assert not writer._background_task.done()  # Verify task is running

    first_file = writer.filename
    await writer.send({"message": "first file"})

    # Move time forward past rollover period
    await asyncio.sleep(3)

    second_file = writer.filename
    await writer.send({"message": "second file"})

    await writer.stop()

    assert first_file != second_file
    assert first_file.exists()
    assert second_file.exists()
    assert "first file" in first_file.read_text()
    assert "second file" in second_file.read_text()
