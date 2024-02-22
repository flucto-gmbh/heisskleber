import asyncio
import sys
from time import time

from heisskleber.udp import AsyncUdpPublisher, AsyncUdpSubscriber, UdpConf


async def publish_forever():
    conf = UdpConf(host="127.0.0.1", port=12345)
    pub = AsyncUdpPublisher(conf)

    while True:
        await asyncio.sleep(1)
        await pub.send({"epoch": time(), "data": "Hello, world!"}, "udp")


async def listen_forever() -> None:
    conf = UdpConf(host="127.0.0.1", port=12345)
    sub = AsyncUdpSubscriber(conf)
    print(f"Started subscriber: {sub}")

    while True:
        _, payload = await sub.receive()
        print(f"Received payload: {payload}")


async def main():
    await asyncio.gather(publish_forever(), listen_forever())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
