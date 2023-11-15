import math
from datetime import datetime, timedelta
from queue import Queue

import numpy as np

from heisskleber.mqtt import MqttSubscriber


def round_dt(dt, delta):
    """Round a datetime object based on a delta timedelta."""
    return datetime.min + math.floor((dt - datetime.min) / delta) * delta


def timestamp_generator(start_epoch, timedelta_in_ms):
    """Generate increasing timestamps based on a start epoch and a delta in ms."""
    timestamp_start = datetime.fromtimestamp(start_epoch)
    delta = timedelta(milliseconds=timedelta_in_ms)
    delta_half = timedelta(milliseconds=timedelta_in_ms // 2)
    next_timestamp = round_dt(timestamp_start, delta) + delta_half
    while True:
        yield datetime.timestamp(next_timestamp)
        next_timestamp += delta


def interpolate(t1, y1, t2, y2, t_target):
    """Perform linear interpolation between two data points."""
    y1, y2 = np.array(y1), np.array(y2)
    fraction = (t_target - t1) / (t2 - t1)
    interpolated_values = y1 + fraction * (y2 - y1)
    return interpolated_values.tolist()


class Resampler:
    """
    Synchronously resample data based on a fixed rate. Can handle upsampling and downsampling.

    Parameters:
    ----------
    config : namedtuple
        Configuration for the resampler.
    subscriber : MqttSubscriber
        Synchronous Subscriber
    """

    def __init__(self, config, subscriber: MqttSubscriber):
        self.config = config
        self.subscriber = subscriber
        self.buffer = Queue()
        self.resample_rate = self.config.resample_rate
        self.delta_t = round(self.resample_rate / 1_000, 3)

    def run(self):
        topic, message = self.subscriber.receive()
        self.buffer.put(self._pack_data(message))
        self.data_keys = message.keys()

        while True:
            topic, message = self.subscriber.receive()
            self.buffer.put(self._pack_data(message))

    def resample(self):
        aggregated_data = []
        aggregated_timestamps = []
        # Get first element to determine timestamp
        timestamp, message = self.buffer.get()
        timestamps = timestamp_generator(timestamp, self.resample_rate)

        # step through interpolation timestamps
        for next_timestamp in timestamps:
            # last_timestamp, last_message = timestamp, message

            # append new data to buffer until the most recent data
            # is newer than the next interplation timestamp
            while timestamp < next_timestamp:
                aggregated_timestamps.append(timestamp)
                aggregated_data.append(message)
                timestamp, message = self.buffer.get()

            return_timestamp = round(next_timestamp - self.delta_t / 2, 3)

            # Case 1: Only one new data point was received
            if len(aggregated_data) == 1:
                last_timestamp, last_message = (
                    aggregated_timestamps[0],
                    aggregated_data[0],
                )

                # Case 1a Upsampling:
                # The data point is not within our time interval
                # We step through time intervals, yielding interpolated data points
                while timestamp - next_timestamp > self.delta_t:
                    last_message = interpolate(
                        last_timestamp,
                        last_message,
                        timestamp,
                        message,
                        return_timestamp,
                    )
                    last_timestamp = return_timestamp
                    return_timestamp += self.delta_t
                    next_timestamp = next(timestamps)
                    yield self._unpack_data(last_timestamp, last_message)

                # Case 1b: The data point is within our time interval
                # We simply yield the data point
                # Note, this will also be the case once we have advanced the time interval by upsampling
                last_message = interpolate(
                    last_timestamp,
                    last_message,
                    timestamp,
                    message,
                    return_timestamp,
                )
                last_timestamp = return_timestamp
                return_timestamp += self.delta_t
                yield self._unpack_data(last_timestamp, last_message)

            # Case 2 - downsampling: Multiple data points were during the resampling timeframe
            # We simply yield the mean of the data points, which is more robust and performant than interpolation
            if len(aggregated_data) > 1:
                # yield self._handle_downsampling(return_timestamp, aggregated_data)
                mean_message = np.mean(np.array(aggregated_data), axis=0)
                yield self._unpack_data(return_timestamp, mean_message)

            # reset the aggregator
            aggregated_data.clear()
            aggregated_timestamps.clear()

    def _handle_downsampling(self, return_timestamp, aggregated_data) -> dict:
        """Handle the downsampling case."""
        mean_message = np.mean(np.array(aggregated_data), axis=0)
        return self._unpack_data(return_timestamp, mean_message)

    def _pack_data(self, data) -> tuple[int, list]:
        # pack data from dict to tuple list
        ts = data.pop("epoch")
        return (ts, list(data.values()))

    def _unpack_data(self, ts, values) -> dict:
        # from tuple
        return {"epoch": round(ts, 3), **dict(zip(self.data_keys, values))}
