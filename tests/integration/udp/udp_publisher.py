from time import sleep

from heisskleber.udp import UdpConf, UdpPublisher


def main() -> None:
    conf = UdpConf(host="localhost", port=12345)
    pub = UdpPublisher(conf)

    while True:
        pub.send({"data": "hello"}, topic="test")
        sleep(1.0)


if __name__ == "__main__":
    main()
