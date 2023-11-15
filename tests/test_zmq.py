from heisskleber.zmq.config import ZmqConf


def test_config_parses_correctly():
    conf = ZmqConf(protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556)
    assert conf.protocol == "tcp"
    assert conf.interface == "localhost"
    assert conf.publisher_port == 5555
    assert conf.subscriber_port == 5556

    assert conf.publisher_address == "tcp://localhost:5555"
    assert conf.subscriber_address == "tcp://localhost:5556"
