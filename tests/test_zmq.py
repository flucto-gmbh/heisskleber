from multiprocessing import Process

from heisskleber import get_sink, get_source
from heisskleber.broker.zmq_broker import zmq_broker
from heisskleber.config import load_config
from heisskleber.zmq.config import ZmqConf
from heisskleber.zmq.config import ZmqConf as BrokerConf
from heisskleber.zmq.publisher import ZmqPublisher
from heisskleber.zmq.subscriber import ZmqSubscriber


def test_config_parses_correctly():
    conf = ZmqConf(protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556)
    assert conf.protocol == "tcp"
    assert conf.interface == "localhost"
    assert conf.publisher_port == 5555
    assert conf.subscriber_port == 5556

    assert conf.publisher_address == "tcp://localhost:5555"
    assert conf.subscriber_address == "tcp://localhost:5556"


def test_instantiate_subscriber():
    conf = ZmqConf(protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556)
    sub = ZmqSubscriber(conf, "test")
    assert sub.config == conf


def test_send_receive():
    # 2. start publisher in extra thread
    # 3. start subscriber in extra thread
    # 4. send message from publisher to broker
    # 5. receive message from broker in subscriber
    # 6. assert that message is the same
    broker_conf = BrokerConf()
    sink = get_sink("zmq")
    source = get_source("zmq", "test")

    print("starting broker")
    broker_p = Process(target=zmq_broker, args=(broker_conf,))
    broker_p.start()

    for i in range(10):
        print(f"sending message {i}")
        sink.send({"message": i}, topic="test")
        print("waiting for receive")
        topic, ret_message = source.receive()
        print(f"received message no. {i} {ret_message}")
        assert topic == "test"
        assert ret_message["message"] == i

    broker_p.terminate()


def test_send_receive_2():
    broker_conf = BrokerConf()
    pub = ZmqPublisher(load_config(ZmqConf(), "zmq"))
    sub = ZmqSubscriber(load_config(ZmqConf(), "zmq"), "test")

    print("starting broker")
    broker_p = Process(target=zmq_broker.zmq_broker, args=(broker_conf,))
    broker_p.start()

    for i in range(10):
        print(f"sending message {i}")
        pub.send({"message": i}, topic="test")
        print("awaiting message")
        t, m = sub.receive()
        print("received message")
        assert t == "test"
        assert m["message"] == i

    del pub
    del sub
    broker_p.terminate()
