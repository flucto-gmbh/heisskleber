import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf
from heisskleber.stream import Resampler, ResamplerConf


async def main():
    conf = MqttConf(broker="localhost", port=1883, user="", password="")
    sub = AsyncMqttSubscriber(conf, topic="#")

    subscriber_task = asyncio.create_task(sub.run())

    resampler = Resampler(ResamplerConf(), sub)

    async for data in resampler.resample():
        print(data)

    subscriber_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
