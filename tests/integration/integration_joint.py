import asyncio

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf
from heisskleber.stream import Joint, ResamplerConf


async def main():
    topic1 = "topic1"
    topic2 = "topic2"

    config = MqttConf(broker="localhost", port=1883, user="", password="")  # not a real password
    sub1 = AsyncMqttSubscriber(config, topic1)
    sub2 = AsyncMqttSubscriber(config, topic2)

    resampler_config = ResamplerConf(resample_rate=250)

    joint = Joint(resampler_config, [sub1, sub2])
    await joint.setup()

    while True:
        data = await joint.receive()
        print(data)


# Run the event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
