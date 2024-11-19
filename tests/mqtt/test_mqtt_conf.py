from heisskleber.mqtt.config import MqttConf, Will


def test_create_config_with_will() -> None:
    config_dict = {
        "host": "example.com",
        "port": 1883,
        "ssl": False,
        "timeout": 60,
        "keep_alive": 60,
        "will": {"topic": "will_topic", "payload": "I didn't make it", "retain": False, "properties": None},
    }

    conf = MqttConf.from_dict(config_dict)

    assert conf.will == Will(topic="will_topic", payload="I didn't make it", retain=False, properties=None)
    assert conf.host == "example.com"
    assert conf.port == 1883
    assert conf.ssl is False
    assert conf.timeout == 60
    assert conf.keep_alive == 60
