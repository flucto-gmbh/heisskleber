from heisskleber.core.types import Source

from .publisher import SerialPublisher


class SerialForwarder:
    def __init__(self, subscriber: Source, publisher: SerialPublisher) -> None:
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
        topic, data = self.sub.receive()

        # We send the topic and let the publisher decide what to do with it
        self.pub.send(data, topic)

    """
    Enter loop and continuously forward messages
    """

    def sub_pub_loop(self) -> None:
        while True:
            self.forward_message()
