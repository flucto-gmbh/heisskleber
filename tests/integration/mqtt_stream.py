import asyncio

from heisskleber.mqtt import MqttConf, MqttSource
from heisskleber.stream import Resampler, ResamplerConf


async def main():
    conf = MqttConf(host="localhost", port=1883, user="", password="")
    sub = MqttSource(conf, topic="#")

    resampler = Resampler(ResamplerConf(), sub)

    while True:
        data = await resampler.receive()
        print(data)


if __name__ == "__main__":
    asyncio.run(main())
