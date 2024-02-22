from heisskleber.udp import UdpConf, UdpSubscriber


def main() -> None:
    conf = UdpConf(host="192.168.137.1", port=6600)
    subscriber = UdpSubscriber(conf)

    while True:
        topic, data = subscriber.receive()
        print(topic, data)


if __name__ == "__main__":
    main()
