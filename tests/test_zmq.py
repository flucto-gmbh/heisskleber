import time
from multiprocessing import Process, Queue

from heisskleber import get_sink, get_source
from heisskleber.broker.zmq_broker import zmq_broker
from heisskleber.config import load_config
from heisskleber.zmq.config import ZmqConf
from heisskleber.zmq.publisher import ZmqPublisher
from heisskleber.zmq.subscriber import ZmqSubscriber


def test_config_parses_correctly():
    conf = ZmqConf(
        protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556
    )
    assert conf.protocol == "tcp"
    assert conf.interface == "localhost"
    assert conf.publisher_port == 5555
    assert conf.subscriber_port == 5556

    assert conf.publisher_address == "tcp://localhost:5555"
    assert conf.subscriber_address == "tcp://localhost:5556"


def test_instantiate_subscriber():
    conf = ZmqConf(
        protocol="tcp", interface="localhost", publisher_port=5555, subscriber_port=5556
    )
    sub = ZmqSubscriber(conf, "test")
    assert sub.config == conf


def test_send_receive():
    zmq_conf = load_config(ZmqConf(), "zmq")
    zmq_conf.verbose = True
    pub = ZmqPublisher(zmq_conf)
    sub = ZmqSubscriber(zmq_conf, "test")

    print(f"subscriber: {sub.__dict__}")
    print(f"publisher: {pub.__dict__}")

    def rec(sub):
        while True:
            t, m = sub.receive()
            print(f"received message: {t}: {m}")

    # q = Queue(maxsize=10)
    sub_p = Process(target=rec, args=(sub,))
    sub_p.start()
    time.sleep(1)

    for i in range(10):
        message = {"message": i}
        pub.send(message, topic="test")
        print(f"message away!")
        time.sleep(1)
        # topic_received, message_received = q.get()
        # assert topic_received == topic
        # assert message_received == message

    sub_p.terminate()


if __name__ == "__main__":
    test_send_receive()
