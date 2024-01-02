import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf
from heisskleber.stream import Resampler, ResamplerConf


async def main():
    conf = MqttConf(broker="localhost", port=1883, user="", password="")
    sub = AsyncMqttSubscriber(conf, topic="#")

    resampler = Resampler(ResamplerConf(), sub)

    while True:
        data = await resampler.receive()
        print(data)


if __name__ == "__main__":
    asyncio.run(main())
