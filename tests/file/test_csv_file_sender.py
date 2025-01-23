from typing import Any

import pytest

from heisskleber.file import FileConf, FileWriter


class CSVPacker:
    def __init__(self):
        self.fields: list[str] = []

    def packer(self, data: dict[str, Any]) -> bytes:
        """Create a string of ordered fields from dictionary values."""
        return ",".join([str(data[field]) for field in self.fields]).encode()

    def header(self, data: dict[str, Any]) -> list[str]:
        """Create header for csv field."""
        self.fields = list(data.keys())
        return [
            "sep=,",
            "#encoding=UTF-8",
            "#datatype:" + ",".join(type(v).__name__ for v in data.values()),
            ",".join(self.fields),
        ]


@pytest.mark.asyncio
async def test_file_writer_csv(tmp_path) -> None:
    """Test file rollover functionality."""
    csv_packer = CSVPacker()
    config = FileConf(rollover=2, name_fmt="%Y%m%d_%H%M%s.txt", directory=str(tmp_path))  # 2 second rollover
    writer: FileWriter[dict[str, Any]] = FileWriter(config, header_func=csv_packer.header, packer=csv_packer.packer)

    await writer.start()
    file = writer.filename

    await writer.send({"epoch": 1, "value": 0.0})
    await writer.send({"value": 0.5, "epoch": 2})

    await writer.stop()

    with file.open("r") as f:
        result = f.readlines()

    assert result[0] == "sep=,\n"
    assert result[1] == "#encoding=UTF-8\n"
    assert result[2] == "#datatype:int,float\n"
    assert result[3] == "epoch,value\n"
    assert result[4] == "1,0.0\n"
    assert result[5] == "2,0.5\n"
