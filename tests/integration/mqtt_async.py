import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf


async def main():
    conf = MqttConf(broker="localhost", port=1883, user="", password="")
    sub = AsyncMqttSubscriber(conf, topic="#")
    # async for topic, message in sub:
    #     print(message)
    _ = asyncio.create_task(sub.start_loop())
    while True:
        topic, message = await sub.receive()
        print(message)


if __name__ == "__main__":
    asyncio.run(main())