import asyncio
import time

from termcolor import colored

from heisskleber.mqtt import AsyncMqttPublisher, MqttConf

colortable = ["red", "green", "yellow", "blue", "magenta", "cyan"]


async def send_every_n_miliseconds(frequency, value, pub, topic):
    start = time.time()
    while True:
        epoch = time.time() - start
        payload = {"epoch": epoch, f"value{value}": value}
        print_message = f"Pub #{int(value)} sending {payload}"
        print(colored(print_message, colortable[int(value)]))
        await pub.send(payload, topic)
        await asyncio.sleep(frequency)


async def main2():
    config = MqttConf(host="localhost", port=1883, user="", password="")

    pubs = [AsyncMqttPublisher(config) for i in range(5)]
    tasks = []
    for i, pub in enumerate(pubs):
        tasks.append(asyncio.create_task(send_every_n_miliseconds(1 + i * 0.1, i, pub, f"topic{i}")))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # main()
    asyncio.run(main2())
