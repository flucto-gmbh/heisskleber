import os
import warnings
from typing import TypeVar

import yaml

from heisskleber.config import BaseConf
from heisskleber.config.cmdline import get_cmdline

ConfigType = TypeVar(
    "ConfigType", bound=BaseConf
)  # https://stackoverflow.com/a/46227137 , https://docs.python.org/3/library/typing.html#typing.TypeVar


def get_config_dir() -> str:
    config_dir = os.path.join(os.path.join(os.environ["HOME"], ".config"), "heisskleber")
    if not os.path.isdir(config_dir):
        warnings.warn(f"no such directory: {config_dir}", stacklevel=2)
        raise FileNotFoundError
    return config_dir


def get_config_filepath(filename: str) -> str:
    config_filepath = os.path.join(get_config_dir(), filename)
    if not os.path.isfile(config_filepath):
        warnings.warn(f"no such file: {config_filepath}", stacklevel=2)
        raise FileNotFoundError
    return config_filepath


def read_yaml_config_file(config_fpath: str) -> dict:
    with open(config_fpath) as config_filehandle:
        return yaml.safe_load(config_filehandle)


def update_config(config: ConfigType, config_dict: dict) -> ConfigType:
    for config_key, config_value in config_dict.items():
        # get expected type of element from config_object:
        if not hasattr(config, config_key):
            error_msg = f"no such configuration parameter: {config_key}, skipping"
            warnings.warn(error_msg, stacklevel=2)
            continue
        cast_func = type(config[config_key])
        try:
            config[config_key] = cast_func(config_value)
        except Exception as e:
            warnings.warn(
                f"failed to cast {config_value} to {type(config[config_key])}: {e}. skipping",
                stacklevel=2,
            )
            continue
    return config


def load_config(config: ConfigType, config_filename: str, read_commandline: bool = True) -> ConfigType:
    """Load the config file and update the config object.

    Parameters
    ----------
    config : BaseConf
        The config object to fill with values.
    config_filename : str
        The name of the config file in $HOME/.config
        If the file does not have an extension the default extension .yaml is appended.
    read_commandline : bool
        Whether to read arguments from the command line. Optional. Defaults to True.
    """
    config_filename = config_filename if "." in config_filename else config_filename + ".yaml"
    config_filepath = get_config_filepath(config_filename)
    config_dict = read_yaml_config_file(config_filepath)
    config = update_config(config, config_dict)

    if not read_commandline:
        return config

    config_dict = get_cmdline()
    config = update_config(config, config_dict)
    return config
