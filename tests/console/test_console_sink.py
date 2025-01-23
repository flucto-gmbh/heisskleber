import pytest

from heisskleber.console import ConsoleConf, ConsoleSender


@pytest.mark.asyncio
async def test_console_sink(capsys) -> None:
    sink = ConsoleSender(ConsoleConf())
    await sink.send({"key": 3}, "test")

    captured = capsys.readouterr()

    assert captured.out == 'test:\t{"key": 3}\n'
