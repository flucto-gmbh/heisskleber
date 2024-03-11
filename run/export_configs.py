from dataclasses import asdict

import yaml

from heisskleber.mqtt.config import MqttConf
from heisskleber.serial.config import SerialConf
from heisskleber.tcp.config import TcpConf
from heisskleber.udp.config import UdpConf
from heisskleber.zmq.config import ZmqConf

configs = {"mqtt": MqttConf(), "zmq": ZmqConf(), "udp": UdpConf(), "tcp": TcpConf(), "serial": SerialConf()}


for name, config in configs.items():
    with open(f"./config/heisskleber/{name}.yaml", "w") as file:
        file.write(f"# Heisskleber config file for {config.__class__.__name__}\n")
        file.write(yaml.dump(asdict(config)))
