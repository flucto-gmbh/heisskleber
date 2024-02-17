import pytest

from heisskleber.console.sink import AsyncConsoleSink, ConsoleSink


def test_console_sink(capsys) -> None:
    sink = ConsoleSink()
    sink.send({"key": 3}, "test")

    captured = capsys.readouterr()

    assert captured.out == "{'key': 3}\n"


def test_console_sink_verbose(capsys) -> None:
    sink = ConsoleSink(verbose=True)
    sink.send({"key": 3}, "test")

    captured = capsys.readouterr()

    assert captured.out == "test:\t{'key': 3}\n"


def test_console_sink_pretty(capsys) -> None:
    sink = ConsoleSink(pretty=True)
    sink.send({"key": 3}, "test")

    captured = capsys.readouterr()

    assert captured.out == '{\n    "key": 3\n}\n'


def test_console_sink_pretty_verbose(capsys) -> None:
    sink = ConsoleSink(pretty=True, verbose=True)
    sink.send({"key": 3}, "test")

    captured = capsys.readouterr()

    assert captured.out == 'test:\t{\n    "key": 3\n}\n'


@pytest.mark.asyncio
async def test_async_console_sink(capsys) -> None:
    sink = AsyncConsoleSink()
    await sink.send({"key": 3}, "test")

    captured = capsys.readouterr()

    assert captured.out == "{'key': 3}\n"
