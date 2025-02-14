import logging
from dataclasses import dataclass
from typing import Literal

import pytest

from heisskleber.core import BaseConf
from heisskleber.core.config import _check_type


@dataclass
class SampleConfig(BaseConf):
    name: str
    age: int = 18
    speed: float = 1.05


def test_config_constructor() -> None:
    test_conf = SampleConfig(name="Gandalf", age=200, speed=10.0)
    assert test_conf.name == "Gandalf"
    assert test_conf.age == 200
    assert test_conf.speed == 10.0


def test_config_from_dict() -> None:
    test_dict = {"name": "Alice", "age": 30, "job": "Electrician", "speed": 1.0}

    expected = SampleConfig(name="Alice", age=30, speed=1.0)

    configuration = SampleConfig.from_dict(test_dict)
    assert configuration == expected


def test_config_from_dict_with_default() -> None:
    test_dict = {"name": "Alice"}

    expected = SampleConfig(name="Alice", age=18)

    configuration = SampleConfig.from_dict(test_dict)
    assert configuration == expected


def test_pytest_raises_type_error() -> None:
    with pytest.raises(TypeError):
        SampleConfig(name=1.0)  # type: ignore[arg-type]


def test_pytest_raises_type_error_from_dict() -> None:
    with pytest.raises(TypeError):
        SampleConfig.from_dict({"name": 1.0, "age": "monkey"})


def test_conf_from_file() -> None:
    test_conf = SampleConfig.from_file("./tests/core/test_conf.yaml")

    assert test_conf.name == "Frodo"
    assert test_conf.age == 30
    assert test_conf.speed == 0.5


@dataclass
class ConfigWithLiteral(BaseConf):
    direction: Literal["U", "D"] = "U"


def test_parses_literal() -> None:
    test_dict = {"direction": "U"}
    expected = ConfigWithLiteral(direction="U")

    config = ConfigWithLiteral.from_dict(test_dict)

    assert config == expected


def test_logs_literal_error(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.ERROR)

    expected = Literal[1, 2, 3]

    with pytest.raises(TypeError):
        _check_type(4, expected)

    assert len(caplog.records) == 1
    assert "4 is not part of (1, 2, 3)" in caplog.text
