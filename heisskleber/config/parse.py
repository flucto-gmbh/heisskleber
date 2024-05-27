import logging
from pathlib import Path
from typing import Any

import yaml

from heisskleber.config.cmdline import get_cmdline
from heisskleber.config.config import Config

log = logging.getLogger(__name__)


def get_config_dir() -> Path:
    config_dir = Path.home() / ".config" / "heisskleber"
    if not config_dir.is_dir():
        log.error(f"no such directory: {config_dir}", stacklevel=2)
        raise FileNotFoundError
    return config_dir


def get_config_filepath(filename: str) -> Path:
    config_filepath = get_config_dir() / filename
    if not config_filepath.is_file():
        log.error(f"no such file: {config_filepath}", stacklevel=2)
        raise FileNotFoundError
    return config_filepath


def read_yaml_config_file(config_fpath: Path) -> dict[str, Any]:
    with config_fpath.open() as config_filehandle:
        return yaml.safe_load(config_filehandle)  # type: ignore [no-any-return]


def update_config(config: Config, config_dict: dict[str, Any]) -> Config:
    for config_key, config_value in config_dict.items():
        if not hasattr(config, config_key):
            error_msg = f"no such configuration parameter: {config_key}, skipping"
            log.info(error_msg, stacklevel=2)
            continue
        cast_func = type(config[config_key])
        try:
            config[config_key] = cast_func(config_value)
        except Exception as e:
            log.warning(
                f"failed to cast {config_value} to {type(config[config_key])}: {e}. skipping",
                stacklevel=2,
            )
            continue
    return config


def load_config(config: Config, config_filename: str, read_commandline: bool = True) -> Config:
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
