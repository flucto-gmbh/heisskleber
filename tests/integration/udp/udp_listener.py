from heisskleber.udp import UdpConf, UdpSubscriber


def main() -> None:
    conf = UdpConf(host="localhost", port=12345)
    sub = UdpSubscriber(conf)

    while True:
        _, payload = sub.receive()
        print(f"Received payload: {payload}")


if __name__ == "__main__":
    main()
