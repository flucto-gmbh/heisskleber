import asyncio

from heisskleber.mqtt import MqttConf, MqttSource


async def main():
    config = MqttConf(host="localhost", port=1883, user="", password="")

    sub = MqttSource(config, topic="#")

    while True:
        topic, data = await sub.receive()
        print(f"topic: {topic}, data: {data}")


if __name__ == "__main__":
    asyncio.run(main())
