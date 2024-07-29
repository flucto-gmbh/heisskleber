import asyncio

from heisskleber.mqtt import MqttConf, MqttSource


async def main():
    conf = MqttConf(host="localhost", port=1883, user="", password="")
    sub = MqttSource(conf, topic="#")
    # async for topic, message in sub:
    #     print(message)
    # _ = asyncio.create_task(sub.run())
    while True:
        topic, message = await sub.receive()
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
