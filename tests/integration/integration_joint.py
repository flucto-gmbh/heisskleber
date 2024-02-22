import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf
from heisskleber.stream import Joint, Resampler, ResamplerConf


async def main():
    topics = ["topic0", "topic1", "topic2", "topic3"]

    config = MqttConf(host="localhost", port=1883, user="", password="")  # not a real password
    subs = [AsyncMqttSubscriber(config, topic=topic) for topic in topics]

    resampler_config = ResamplerConf(resample_rate=1000)

    joint = Joint(resampler_config, [Resampler(resampler_config, sub) for sub in subs])

    while True:
        data = await joint.receive()
        print(data)


# Run the event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
