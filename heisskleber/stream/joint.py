import asyncio

from heisskleber.core.types import AsyncSubscriber
from heisskleber.stream.resampler import Resampler, ResamplerConf


class Joint:
    """Joint that takes multiple async streams and synchronizes them based on their timestamps.

    Note that you need to run the setup() function first to initialize the

    Parameters:
    ----------
    conf : ResamplerConf
        Configuration for the joint.
    subscribers : list[AsyncSubscriber]
        List of asynchronous subscribers.

    """

    def __init__(self, conf: ResamplerConf, subscribers: list[AsyncSubscriber]):
        self.conf = conf
        self.subscribers = subscribers
        self.generators = []
        self.resampler_timestamps = []
        self.latest_timestamp = 0
        self.latest_data = {}
        self.tasks = []

    async def receive(self):
        old_value = self.latest_data.copy()
        await self._update()
        return old_value

    async def generate(self):
        while True:
            yield self.latest_data
            await self._update()

    """Set up the streamer joint, which will activate all subscribers."""

    async def setup(self):
        for sub in self.subscribers:
            # Start an async task to run the subscriber loop
            task = asyncio.create_task(sub.run())
            self.tasks.append(task)
            self.generators.append(Resampler(self.conf, sub).resample())

        await self._synchronize()

    async def _synchronize(self):
        data = {}
        # first pass to initialize resamplers
        for resampler in self.generators:
            data = await anext(resampler)
            self.resampler_timestamps.append(data["epoch"])

            if data["epoch"] > self.latest_timestamp:
                self.latest_timestamp = data["epoch"]
                self.latest_data = dict(data)

        for resampler, timestamp in zip(self.generators, self.resampler_timestamps):
            if timestamp == self.latest_timestamp:
                continue

            while timestamp < self.latest_timestamp:
                data = await anext(resampler)
                timestamp = data["epoch"]

            self.latest_data.update(data)

    async def _update(self):
        data: dict = {}
        for resampler in self.generators:
            try:
                data = await anext(resampler)

                if data["epoch"] >= self.latest_timestamp:
                    self.latest_timestamp = data["epoch"]
                    self.latest_data.update(data)
            except Exception:
                print(Exception)
