import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf


async def main():
    config = MqttConf(host="localhost", port=1883, user="", password="")

    sub = AsyncMqttSubscriber(config, topic="#")

    while True:
        topic, data = await sub.receive()
        print(f"topic: {topic}, data: {data}")


if __name__ == "__main__":
    asyncio.run(main())
