import asyncio
import time
from random import random

from heisskleber.mqtt import AsyncMqttPublisher, MqttConf, MqttPublisher


def main():
    config = MqttConf(broker="localhost", port=1883, user="", password="")
    pub = MqttPublisher(config)
    pub2 = MqttPublisher(config)

    timestamp = 0
    dt1 = 0.7
    dt2 = 0.5
    t1 = 0
    t2 = 5
    while True:
        dt = random()  # noqa: S311
        timestamp += dt
        print(f"timestamp at {timestamp} s")

        while timestamp - t1 > dt1:
            t1 = timestamp + dt1
            pub.send({"value1": 1 + dt, "epoch": timestamp}, "topic1")
            print("Pub1 sending")
        while timestamp - t2 > dt2:
            t2 = timestamp + dt2
            pub2.send({"value2": 2 - dt, "epoch": timestamp}, "topic2")
            print("Pub2 sending")
        time.sleep(dt)


async def send_every_n_miliseconds(frequency, value, pub, topic):
    start = time.time()
    while True:
        epoch = time.time() - start
        await pub.send({"epoch": epoch, f"value{value}": value}, topic)
        await asyncio.sleep(frequency)


async def main2():
    config = MqttConf(broker="localhost", port=1883, user="", password="")

    pubs = [AsyncMqttPublisher(config) for i in range(5)]
    tasks = []
    for i, pub in enumerate(pubs):
        tasks.append(asyncio.create_task(send_every_n_miliseconds(1 + i * 0.1, i, pub, f"topic{i}")))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # main()
    asyncio.run(main2())
