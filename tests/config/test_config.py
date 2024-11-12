from dataclasses import dataclass

import pytest

from heisskleber.config.config import BaseConf


@dataclass
class TestConf(BaseConf):
    name: str
    age: int = 18
    speed: float = 1.05


def test_config_from_dict():
    test_dict = {"name": "Alice", "age": 30, "job": "Electrician", "speed": 1.0}

    expected = TestConf(name="Alice", age=30, speed=1.0)

    configuration = TestConf.from_dict(test_dict)
    assert configuration == expected


def test_config_from_dict_with_default():
    test_dict = {"name": "Alice"}

    expected = TestConf(name="Alice", age=18)

    configuration = TestConf.from_dict(test_dict)
    assert configuration == expected


def test_pytest_raises_type_error():
    with pytest.raises(TypeError):
        TestConf(name=1.0)


def test_pytest_raises_type_error_from_dict():
    with pytest.raises(TypeError):
        TestConf.from_dict({"name": 1.0, "age": "monkey"})
