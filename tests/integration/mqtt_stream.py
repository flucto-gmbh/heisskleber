import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf
from heisskleber.stream import Resampler, ResamplerConf


async def main():
    conf = MqttConf(broker="localhost", port=1883, user="", password="")
    sub = AsyncMqttSubscriber(conf, topic="#")
    # async for topic, message in sub:
    #     print(message)
    subscriber_task = asyncio.create_task(sub.start_loop())

    resampler = Resampler(ResamplerConf(), sub)
    resampler_task = asyncio.create_task(resampler.run())

    async for data in resampler.resample():
        print(data)

    subscriber_task.cancel()
    resampler_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
