from heisskleber.broker import start_zmq_broker
from heisskleber.config import load_config
from heisskleber.zmq.config import ZmqConf as BrokerConf

if __name__ == "__main__":
    broker_config = load_config(BrokerConf(), "zmq")
    start_zmq_broker(config=broker_config)
