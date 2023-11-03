import socket

from heisskleber.network.packer import get_packer
from heisskleber.network.pubsub.types import Publisher
from heisskleber.network.udp.config import UDPConf


class UDP_Publisher(Publisher):
    def __init__(self, config):
        self.config = config
        self.ip = self.config.ip
        self.port = self.config.port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packer = get_packer(self.config.packer)

    def send(self, topic, message):
        payload = self.packer(message)
        payload = payload.encode("utf-8")
        self.socket.sendto(payload, (self.ip, self.port))

    def __del__(self):
        self.socket.close()


def udp_sender():
    target_ip = "127.0.0.1"  # Replace this with the receiver's IP address
    target_port = 12345  # Replace this with the receiver's port number

    message = "Hello, UDP Receiver!"

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send the message to the receiver
        udp_socket.sendto(message.encode("utf-8"), (target_ip, target_port))
        print("Message sent successfully!")
    except Exception as e:
        print("Error occurred while sending the message:", str(e))
    finally:
        udp_socket.close()


if __name__ == "__main__":
    conf = UDPConf(ip="192.168.1.122", port=12345)
    pub = UDP_Publisher(conf)

    pub.send("test", {"test": "test"})
    # pub.send("test", "Hi from pub")
