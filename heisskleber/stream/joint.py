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
        self.output_task = asyncio.create_task(self.output_work())
        self.combined_dict: dict[str, Serializable] = {}

    """
    Main interaction coroutine: Get next value out of the queue.
    """

    async def receive(self) -> dict[str, Any]:
        output = await self.output_queue.get()
        return output

    async def sync(self) -> None:
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
