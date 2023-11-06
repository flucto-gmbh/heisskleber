from heisskleber.core.types import Subscriber

from .publisher import SerialPublisher


class SerialForwarder:
    def __init__(self, subscriber: Subscriber, publisher: SerialPublisher) -> None:
        self.sub = subscriber
        self.pub = publisher

    """
    Wait for message and forward
    """

    def forward_message(self) -> None:
        # collected = {}
        # for sub in self.sub:
        #     topic, data = sub.receive()
        #     collected.update(data)
        _, collected = self.sub.receive()

        self.pub.send("", collected)

    """
    Enter loop and continuously forward messages
    """

    def sub_pub_loop(self) -> None:
        while True:
            self.forward_message()
