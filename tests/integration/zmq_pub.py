import time

from heisskleber import get_sink


def main():
    sink = get_sink("zmq")

    i = 0
    while True:
        sink.send({"test pub": i}, "test")
        time.sleep(1)
        i += 1


if __name__ == "__main__":
    main()
