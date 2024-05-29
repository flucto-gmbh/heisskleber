import unittest.mock as mock
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from heisskleber.config import BaseConf
from heisskleber.config.config import Config
from heisskleber.config.parse import (
    get_cmdline,
    get_config_dir,
    get_config_filepath,
    load_config,
    read_yaml_config_file,
    update_config,
)


@pytest.fixture
def mock_home(monkeypatch):
    home = Path("/mock/home")
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


@pytest.fixture
def mock_config_dir(mock_home):
    with (
        patch("heisskleber.config.parse.get_config_dir", return_value=mock_home / ".config" / "heisskleber"),
        patch("pathlib.Path.is_dir", return_value=True),
    ):
        yield


def test_get_config_dir(mock_home):
    with patch("pathlib.Path.is_dir", return_value=True):
        config_dir = get_config_dir()
    assert config_dir == mock_home / ".config" / "heisskleber"


def test_get_config_dir_not_exists():
    with patch("pathlib.Path.is_dir", return_value=False), pytest.raises(FileNotFoundError):
        get_config_dir()


def test_get_config_filepath(mock_home, mock_config_dir):
    filename = "config.yaml"
    expected_path = mock_home / ".config" / "heisskleber" / filename

    with patch("pathlib.Path.is_file", return_value=True):
        config_filepath = get_config_filepath(filename)

    assert config_filepath == expected_path


def test_update_config():
    @dataclass
    class MockConf(BaseConf):
        existing_key: str = "old"

    config = MockConf(existing_key="old_value")
    config_dict = {"existing_key": "new_value", "non_existing_key": "value"}

    updated_config = update_config(config, config_dict)

    assert updated_config.existing_key == "new_value"


def test_load_config_no_cmdline(mock_home):
    config = MagicMock(spec=Config)
    config_dict = {"key": "value"}
    filename = "config"
    filepath = mock_home / ".config" / "heisskleber" / (filename + ".yaml")

    with (
        patch("heisskleber.config.parse.get_config_dir", return_value=mock_home / ".config" / "heisskleber"),
        patch("heisskleber.config.parse.get_config_filepath", return_value=filepath),
        patch("heisskleber.config.parse.read_yaml_config_file", return_value=config_dict),
        patch("heisskleber.config.parse.update_config", return_value=config) as mock_update_config,
    ):
        result = load_config(config, filename, read_commandline=False)

    mock_update_config.assert_called_with(config, config_dict)
    assert result == config


def test_file_exists():
    with pytest.raises(FileNotFoundError):
        get_config_filepath("i_do_not_exist.yaml")


def test_read_yaml_config_file():
    config_dict = read_yaml_config_file(Path("tests/config.yaml"))
    assert config_dict["verbose"] is True
    assert config_dict["print_stdout"] is False


def test_get_cmdline_patch_argv():
    with mock.patch("sys.argv", ["test.py", "--verbose"]):
        assert get_cmdline()["verbose"] is True


def test_get_cmdline():
    assert (
        get_cmdline(
            [
                "--verbose",
            ]
        )["verbose"]
        is True
    )


def test_load_config_from_file():
    with mock.patch("heisskleber.config.parse.get_config_filepath", return_value=Path("tests/config.yaml")):
        conf = load_config(BaseConf(), "config", read_commandline=False)
        assert conf.verbose is True


def test_load_config_from_yaml():
    with mock.patch("heisskleber.config.parse.get_config_filepath", return_value=Path("tests/config.yaml")), mock.patch(
        "sys.argv", ["test.py", "--print-stdout"]
    ):
        conf = load_config(BaseConf(), "config")
        assert conf.verbose is True
        assert conf.print_stdout is True
