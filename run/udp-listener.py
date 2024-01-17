from heisskleber.udp import UdpSubscriber, UdpConf


def main() -> None:
    conf = UdpConf(ip="192.168.137.1", port=6600)
    subscriber = UdpSubscriber(conf)

    while True:
        topic, data = subscriber.receive()
        print(topic, data)


if __name__ == "__main__":
    main()

