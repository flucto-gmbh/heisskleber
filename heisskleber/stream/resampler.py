import asyncio
import math
from datetime import datetime, timedelta

import numpy as np

from heisskleber.mqtt import AsyncMqttSubscriber


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
    Async resample data based on a fixed rate. Can handle upsampling and downsampling.

    Parameters:
    ----------
    config : namedtuple
        Configuration for the resampler.
    subscriber : AsyncMQTTSubscriber
        Asynchronous Subscriber
    """

    def __init__(self, config, subscriber: AsyncMqttSubscriber):
        self.config = config
        self.subscriber = subscriber
        # TODO: remove buffer
        self.buffer = asyncio.Queue()
        self.resample_rate = self.config.resample_rate
        self.delta_t = round(self.resample_rate / 1_000, 3)

    async def run(self):
        topic, message = await self.subscriber.receive()
        await self.buffer.put(self._pack_data(message))
        self.data_keys = message.keys()

        while True:
            topic, message = await self.subscriber.receive()
            await self.buffer.put(self._pack_data(message))

    async def resample(self):
        aggregated_data = []
        aggregated_timestamps = []
        # Get first element to determine timestamp
        timestamp, message = await self.buffer.get()
        timestamps = timestamp_generator(timestamp, self.resample_rate)

        # step through interpolation timestamps
        for next_timestamp in timestamps:
            # last_timestamp, last_message = timestamp, message

            # await new data and append to buffer until the most recent data
            # is newer than the next interplation timestamp
            while timestamp < next_timestamp:
                aggregated_timestamps.append(timestamp)
                aggregated_data.append(message)
                timestamp, message = await self.buffer.get()
                # topic, message = await self.subscriber.receive()
                # timestamp, message = self._pack_data(message)

            return_timestamp = round(next_timestamp - self.delta_t / 2, 3)

            # Only one new data point was received
            if len(aggregated_data) == 1:
                last_timestamp, last_message = (
                    aggregated_timestamps[0],
                    aggregated_data[0],
                )

                # Case 2 Upsampling:
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

            if len(aggregated_data) > 1:
                # Case 4 - downsampling: Multiple data points were during the resampling timeframe
                yield self._handle_downsampling(return_timestamp, aggregated_data)

            # reset the aggregator
            aggregated_data.clear()
            aggregated_timestamps.clear()

    def _handle_upsampling(self):
        pass

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
