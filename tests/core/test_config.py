from dataclasses import dataclass

import pytest

from heisskleber.core import BaseConf


@dataclass
class TestConf(BaseConf):
    name: str
    age: int = 18
    speed: float = 1.05


def test_config_constructor() -> None:
    test_conf = TestConf(name="Gandalf", age=200, speed=10.0)
    assert test_conf.name == "Gandalf"
    assert test_conf.age == 200
    assert test_conf.speed == 10.0


def test_config_from_dict() -> None:
    test_dict = {"name": "Alice", "age": 30, "job": "Electrician", "speed": 1.0}

    expected = TestConf(name="Alice", age=30, speed=1.0)

    configuration = TestConf.from_dict(test_dict)
    assert configuration == expected


def test_config_from_dict_with_default() -> None:
    test_dict = {"name": "Alice"}

    expected = TestConf(name="Alice", age=18)

    configuration = TestConf.from_dict(test_dict)
    assert configuration == expected


def test_pytest_raises_type_error() -> None:
    with pytest.raises(TypeError):
        TestConf(name=1.0)  # type: ignore[arg-type]


def test_pytest_raises_type_error_from_dict() -> None:
    with pytest.raises(TypeError):
        TestConf.from_dict({"name": 1.0, "age": "monkey"})


def test_conf_from_file() -> None:
    test_conf = TestConf.from_file("./tests/core/test_conf.yaml")

    assert test_conf.name == "Frodo"
    assert test_conf.age == 30
    assert test_conf.speed == 0.5