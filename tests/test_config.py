import os
import unittest.mock as mock

import pytest

from heisskleber.config.parse import (
    get_config_dir,
    get_config_filepath,
    read_yaml_config_file,
)


def test_get_config_dir():
    with mock.patch("os.path.isdir", return_value=True):
        assert get_config_dir() == os.path.join(os.path.join(os.environ["HOME"], ".config"), "heisskleber")


def test_get_config_filepath():
    with mock.patch("os.path.isfile", return_value=True):
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
    # TODO test update_config
    pass


def test_load_config():
    # TODO test load_config
    pass
