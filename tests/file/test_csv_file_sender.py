from typing import Any

import pytest

from heisskleber.file import FileConf, FileWriter


class MyPacker:
    def __init__(self) -> None:
        self.fields: list[str] = []

    def packer(self, data: dict[str, Any]) -> bytes:
        """Create a string of ordered fields from dictionary values."""
        return ";".join([str(data[field]) for field in self.fields]).encode()

    def header(self, data: dict[str, Any]) -> list[str]:
        """Create header for csv field."""
        self.fields = list(data.keys())
        return ["#header"]


@pytest.mark.asyncio
async def test_file_writer_custom_bytes_packer(tmp_path) -> None:
    """Test file rollover functionality."""
    my_packer = MyPacker()
    config = FileConf(rollover=2, name_fmt="%Y%m%d_%H%M%s.txt", directory=str(tmp_path))  # 2 second rollover
    writer = FileWriter(config, header_func=my_packer.header, packer=my_packer.packer)

    await writer.start()
    file = writer.filename

    await writer.send({"epoch": 1, "value": 0.0})
    await writer.send({"value": 0.5, "epoch": 2})

    await writer.stop()

    with file.open("r") as f:
        result = f.readlines()

    assert result[0].strip() == "#header"
    assert result[1].strip() == "1;0.0"
    assert result[2].strip() == "2;0.5"


@pytest.mark.asyncio
async def test_file_writer_json(tmp_path) -> None:
    """Test file rollover functionality."""
    config = FileConf(rollover=2, name_fmt="%Y%m%d_%H%M%s.txt", directory=str(tmp_path), format="json")
    writer = FileWriter(config)

    await writer.start()
    file = writer.filename

    await writer.send({"epoch": 1, "value": 0.0})
    await writer.send({"value": 0.5, "epoch": 2})

    await writer.stop()

    with file.open("r") as f:
        result = f.readlines()

    assert result[0].strip() == '{"epoch": 1, "value": 0.0}'
    assert result[1].strip() == '{"value": 0.5, "epoch": 2}'


@pytest.mark.asyncio
async def test_file_writer_csv_automatic_generation(tmp_path) -> None:
    """Test file rollover functionality."""
    config = FileConf(rollover=2, name_fmt="%Y%m%d_%H%M%s.txt", directory=str(tmp_path), format="csv")
    writer = FileWriter(config)

    await writer.start()
    file = writer.filename

    await writer.send({"epoch": 1, "value": 0.0, "key": "weather"})
    await writer.send({"value": 0.5, "epoch": 2, "key": "weather"})
    await writer.send({"epoch": 3, "key": "weather"})

    await writer.stop()

    with file.open("r") as f:
        result = f.readlines()

    assert result[0].strip() == "sep=,"
    assert result[1].strip() == "#encoding=UTF-8"
    assert result[2].strip() == "#datatype:int,float,str"
    assert result[3].strip() == "epoch,value,key"
    assert result[4].strip() == "1,0.0,weather"
    assert result[5].strip() == "2,0.5,weather"
    assert result[6].strip() == "3,,weather"
