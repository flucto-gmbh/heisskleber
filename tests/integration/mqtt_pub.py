from heisskleber.mqtt import MqttConf, MqttPublisher
import time
from random import random


def main():
    config = MqttConf(broker="localhost", port=1883, user="", password="")
    pub = MqttPublisher(config)
    pub2 = MqttPublisher(config)

    timestamp = 0
    dt1 = 0.7
    dt2 = 0.5
    t1 = 0
    t2 = 5
    while True:
        dt = random()
        timestamp += dt
        print(f"timestamp at {timestamp} s")

        while timestamp - t1 > dt1:
            t1 = timestamp + dt1
            pub.send({"value": 1 + dt, "epoch": timestamp}, "topic1")
            print("Pub1 sending")
        while timestamp - t2 > dt2:
            t2 = timestamp + dt2
            pub2.send({"value": 2 - dt, "epoch": timestamp}, "topic2")
            print("Pub2 sending")
        time.sleep(dt)


if __name__ == "__main__":
    main()
