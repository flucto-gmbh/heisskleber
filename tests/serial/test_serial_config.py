from heisskleber.serial import SerialConf


def test_serial_config() -> None:
    config_dict = {"port": "/test/serial", "baudrate": 5000, "parity": "N", "stopbits": 1}

    config = SerialConf.from_dict(config_dict)

    assert config == SerialConf(port="/test/serial", baudrate=5000, parity="N", stopbits=1)
