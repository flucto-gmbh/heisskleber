import threading
from collections import namedtuple

from heisskleber.mqtt import MqttConf, MqttSubscriber
from heisskleber.stream.sync_resampler import Resampler


def main():
    # topic1 = "/msb-fwd-body/imu"
    # topic2 = "/msb-102-a/imu"
    # topic2 = "/msb-102-a/rpy"
    topic1 = "topic1"
    # topic2 = "topic2"

    config = MqttConf(
        host="localhost", port=1883, user="", password=""
    )  # , not a real password port=1883, user="", password="")
    sub1 = MqttSubscriber(config, topic1)
    # sub2 = MqttSubscriber(config, topic2)

    resampler_config = namedtuple("config", "resample_rate")(1000)

    resampler1 = Resampler(resampler_config, sub1)

    t1 = threading.Thread(target=resampler1.run)
    t1.start()

    # async for resampled_dict in resampler2.resample():
    #     print(resampled_dict)

    try:
        for m1 in zip(resampler1.resample()):
            print(m1)
    finally:
        t1.join()


if __name__ == "__main__":
    main()
