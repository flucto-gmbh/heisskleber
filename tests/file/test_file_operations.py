import json

import pytest

# from freezegun import freeze_time
from heisskleber.file import FileConf, FileWriter


@pytest.fixture
def config():
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
    assert writer._rollover_task is not None

    # Test writing data
    test_data = {"message": "hello world"}
    await writer.send(test_data)

    # Test file content
    current_file = writer._get_filename()
    assert current_file.exists()

    await writer.stop()
    assert writer._current_file is None
    assert writer._rollover_task is None

    # Verify file content after closing
    content = current_file.read_text().split("\n")[0]
    assert content == json.dumps(test_data)
