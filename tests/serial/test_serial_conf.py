from heisskleber.serial import SerialConf


def test_serial_conf() -> None:
    conf = SerialConf()

    assert hasattr(conf, "port")
    assert hasattr(conf, "baudrate")
    assert hasattr(conf, "bytesize")
    assert hasattr(conf, "encoding")
