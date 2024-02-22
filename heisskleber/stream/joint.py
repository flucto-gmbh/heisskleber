import asyncio
from typing import Any

from heisskleber.core.types import Serializable
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

    def __init__(self, conf: ResamplerConf, resamplers: list[Resampler]):
        self.conf = conf
        self.resamplers = resamplers
        self.output_queue: asyncio.Queue[dict[str, Serializable]] = asyncio.Queue()
        self.initialized = asyncio.Event()
        self.initalize_task = asyncio.create_task(self.sync())
        self.combined_dict: dict[str, Serializable] = {}
        self.task: asyncio.Task[None] | None = None

    def __repr__(self) -> str:
        return f"""Joint(resample_rate={self.conf.resample_rate},
        sources={len(self.resamplers)} of type(s): {{r.__class__.__name__ for r in self.resamplers}})"""

    def start(self) -> None:
        self.task = asyncio.create_task(self.output_work())

    def stop(self) -> None:
        if self.task:
            self.task.cancel()

    async def receive(self) -> dict[str, Any]:
        """
        Main interaction coroutine: Get next value out of the queue.
        """
        if not self.task:
            self.start()
        output = await self.output_queue.get()
        return output

    async def sync(self) -> None:
        """Synchronize the resamplers by pulling data from each until the timestamp is aligned. Retains first matching data."""
        print("Starting sync")
        datas = await asyncio.gather(*[source.receive() for source in self.resamplers])
        print("Got data")
        output_data = {}
        data = {}

        latest_timestamp: float = 0.0
        timestamps = []

        print("Syncing...")
        for data in datas:
            if not isinstance(data["epoch"], float):
                error = "Timestamps must be floats"
                raise TypeError(error)

            ts = float(data["epoch"])

            print(f"Syncing..., got {ts}")

            timestamps.append(ts)
            if ts > latest_timestamp:
                latest_timestamp = ts

                # only take the piece of the latest data
                output_data = data

        for resampler, ts in zip(self.resamplers, timestamps):
            while ts < latest_timestamp:
                data = await resampler.receive()
                ts = float(data["epoch"])

            output_data.update(data)

        await self.output_queue.put(output_data)

        print("Finished initalization")
        self.initialized.set()

    """
    Coroutine that waits for new queue data and updates dict.
    """

    async def update_dict(self, resampler: Resampler) -> None:
        data = await resampler.receive()
        if self.combined_dict and self.combined_dict["epoch"] != data["epoch"]:
            print("Oh shit, this is bad!")
        self.combined_dict.update(data)

    """
    Output worker: iterate through queues, read data and join into output queue.
    """

    async def output_work(self) -> None:
        print("Output worker waiting for intitialization")
        await self.initialized.wait()
        print("Output worker resuming")

        while True:
            self.combined_dict = {}
            tasks = [asyncio.create_task(self.update_dict(res)) for res in self.resamplers]
            await asyncio.gather(*tasks)
            await self.output_queue.put(self.combined_dict)
