import os
import unittest.mock as mock

import pytest

from heisskleber.config import BaseConf
from heisskleber.config.parse import (
    get_cmdline,
    get_config_dir,
    get_config_filepath,
    load_config,
    read_yaml_config_file,
    update_config,
)


def test_get_config_dir():
    with mock.patch("os.path.isdir", return_value=True):
        assert get_config_dir() == os.path.join(os.path.join(os.environ["HOME"], ".config"), "heisskleber")


def test_get_config_filepath():
    with mock.patch("os.path.isfile", return_value=True), mock.patch("os.path.isdir", return_value=True):
        assert get_config_filepath("test_config.yaml") == os.path.join(
            os.path.join(os.environ["HOME"], ".config"),
            "heisskleber",
            "test_config.yaml",
        )


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_file_exists():
    with pytest.raises(FileNotFoundError):
        get_config_filepath("i_do_not_exist.yaml")


def test_read_yaml_config_file():
    config_dict = read_yaml_config_file("tests/config.yaml")
    assert config_dict["verbose"] is True
    assert config_dict["print_stdout"] is False


def test_update_config():
    conf_obj = BaseConf()
    conf_obj["verbose"] = False
    conf_obj["print_stdout"] = False
    conf_dict = {"verbose": True, "print_stdout": True}
    conf_obj = update_config(conf_obj, conf_dict)

    assert conf_obj.verbose is True
    assert conf_obj.print_stdout is True


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
    with mock.patch("heisskleber.config.parse.get_config_filepath", return_value="tests/config.yaml"):
        conf = load_config(BaseConf(), "config", read_commandline=False)
        assert conf.verbose is True


def test_load_config():
    with mock.patch("heisskleber.config.parse.get_config_filepath", return_value="tests/config.yaml"), mock.patch(
        "sys.argv", ["test.py", "--print-stdout"]
    ):
        conf = load_config(BaseConf(), "config")
        assert conf.verbose is True
        assert conf.print_stdout is True
