import asyncio

import numpy as np

from heisskleber.mqtt import AsyncMqttSubscriber, MqttConf
from heisskleber.stream.resampler import Resampler, ResamplerConf


async def main():
    # topic1 = "/msb-fwd-body/imu"
    # topic2 = "/msb-102-a/imu"
    # topic2 = "/msb-102-a/rpy"
    topic1 = "topic1"
    topic2 = "topic2"

    config = MqttConf(broker="localhost", port=1883, user="", password="")  # not a real password
    sub1 = AsyncMqttSubscriber(config, topic1)
    sub2 = AsyncMqttSubscriber(config, topic2)

    resampler_config = ResamplerConf(resample_rate=250)

    resampler1 = Resampler(resampler_config, sub1)
    resampler2 = Resampler(resampler_config, sub2)

    _ = asyncio.create_task(sub1.run())
    _ = asyncio.create_task(sub2.run())

    # async for resampled_dict in resampler2.resample():
    #     print(resampled_dict)

    gen1 = resampler1.resample()
    gen2 = resampler2.resample()

    while True:
        m1 = await anext(gen1)
        m2 = await anext(gen2)

        print(f"epoch: {m1['epoch']}")
        print(f"diff: {diff(m1, m2)}")


def diff(dict1, dict2):
    return dict(
        zip(
            dict1.keys(),
            np.array(list(dict1.values())) - np.array(list(dict2.values())),
        )
    )


# Run the event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
