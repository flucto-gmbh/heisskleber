import math
from asyncio import Queue, Task, create_task
from collections.abc import Generator
from datetime import datetime, timedelta

import numpy as np

from heisskleber.core.types import AsyncSource, Serializable

from .config import ResamplerConf


def floor_dt(dt: datetime, delta: timedelta) -> datetime:
    """Round a datetime object based on a delta timedelta."""
    return datetime.min + math.floor((dt - datetime.min) / delta) * delta


def timestamp_generator(start_epoch: float, timedelta_in_ms: int) -> Generator[float, None, None]:
    """Generate increasing timestamps based on a start epoch and a delta in ms.
    The timestamps are meant to be used with the resampler and generator half delta offsets of the returned timetsamps.
    """
    timestamp_start = datetime.fromtimestamp(start_epoch)
    delta = timedelta(milliseconds=timedelta_in_ms)
    delta_half = timedelta(milliseconds=timedelta_in_ms // 2)
    next_timestamp = floor_dt(timestamp_start, delta) + delta_half
    while True:
        yield datetime.timestamp(next_timestamp)
        next_timestamp += delta


def interpolate(t1: float, y1: list[float], t2: float, y2: list[float], t_target: float) -> list[float]:
    """Perform linear interpolation between two data points."""
    y1_array, y2_array = np.array(y1), np.array(y2)
    fraction = (t_target - t1) / (t2 - t1)
    interpolated_values = y1_array + fraction * (y2_array - y1_array)
    return interpolated_values.tolist()


def check_dict(data: dict[str, Serializable]) -> None:
    """Check that only numeric types are in input data."""
    for key, value in data.items():
        if not isinstance(value, (int, float)):
            error_msg = f"Value {value} for key {key} is not of type int or float"
            raise TypeError(error_msg)


class Resampler:
    """
    Async resample data based on a fixed rate. Can handle upsampling and downsampling.

    Methods:
    --------
    start()
        Start the resampler task.

    stop()
        Stop the resampler task.

    receive()
        Get next resampled dictonary from the resampler.
    """

    def __init__(self, config: ResamplerConf, subscriber: AsyncSource) -> None:
        """
        Parameters:
        ----------
        config : namedtuple
            Configuration for the resampler.
        subscriber : AsyncMQTTSubscriber
            Asynchronous Subscriber

        """
        self.config = config
        self.subscriber = subscriber
        self.resample_rate = self.config.resample_rate
        self.delta_t = round(self.resample_rate / 1_000, 3)
        self.message_queue: Queue[dict[str, float]] = Queue(maxsize=50)
        self.resample_task: None | Task[None] = None

    def start(self) -> None:
        """
        Start the resampler task.
        """
        self.resample_task = create_task(self.resample())

    def stop(self) -> None:
        """
        Stop the resampler task
        """
        if self.resample_task:
            self.resample_task.cancel()

    async def receive(self) -> dict[str, float]:
        """
        Get next resampled dictonary from the resampler.

        Implicitly starts the resampler if not already running.
        """
        if not self.resample_task:
            self.start()
        return await self.message_queue.get()

    async def resample(self) -> None:
        """
        Resample data based on a fixed rate.

        Can handle upsampling and downsampling.
        Data will always be centered around the output resample timestamp.
        (i.e. for data returned for t = 1.0s, the data will be resampled for [0.5, 1.5]s)
        """

        print("Starting resampler")
        aggregated_data = []
        aggregated_timestamps = []

        # Get first element to determine timestamp
        topic, data = await self.subscriber.receive()

        check_dict(data)

        timestamp, message = self._pack_data(data)  # type: ignore [arg-type]
        timestamps = timestamp_generator(timestamp, self.resample_rate)
        print(f"Got first element {topic}: {data}")

        # Set data keys to reconstruct dict later
        self.data_keys = data.keys()
        self.topic = topic

        # step through interpolation timestamps
        for next_timestamp in timestamps:
            # await new data and append to buffer until the most recent data
            # is newer than the next interplation timestamp
            while timestamp < next_timestamp:
                aggregated_timestamps.append(timestamp)
                aggregated_data.append(message)

                topic, data = await self.subscriber.receive()
                timestamp, message = self._pack_data(data)  # type: ignore [arg-type]

            return_timestamp = round(next_timestamp - self.delta_t / 2, 3)

            # Only one new data point was received
            if len(aggregated_data) == 1:
                self._is_upsampling = False
                # print("Only one data point")
                last_timestamp, last_message = (
                    aggregated_timestamps[0],
                    aggregated_data[0],
                )

                # Case 2 Upsampling:
                while timestamp - next_timestamp > self.delta_t:
                    self._is_upsampling = True
                    # print("Upsampling")
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
                    await self.message_queue.put(self._unpack_data(last_timestamp, last_message))

                if self._is_upsampling:
                    last_message = interpolate(
                        last_timestamp,
                        last_message,
                        timestamp,
                        message,
                        return_timestamp,
                    )
                last_timestamp = return_timestamp

                await self.message_queue.put(self._unpack_data(last_timestamp, last_message))

            if len(aggregated_data) > 1:
                # Case 4 - downsampling: Multiple data points were during the resampling timeframe
                mean_message = np.mean(np.array(aggregated_data), axis=0)
                await self.message_queue.put(self._unpack_data(return_timestamp, mean_message))

            # reset the aggregator
            aggregated_data.clear()
            aggregated_timestamps.clear()

    def _pack_data(self, data: dict[str, float]) -> tuple[float, list[float]]:
        # pack data from dict to tuple list
        ts = data.pop("epoch")
        return (ts, list(data.values()))

    def _unpack_data(self, ts: float, values: list[float]) -> dict[str, float]:
        # from tuple
        return {"epoch": round(ts, 3), **dict(zip(self.data_keys, values))}
