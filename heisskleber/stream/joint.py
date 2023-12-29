import asyncio

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
        self.input_queues = [asyncio.Queue() for _ in self.resamplers]
        self.output_queue = asyncio.Queue()

        self.initialized = asyncio.Event()
        self.initalize_task = asyncio.create_task(self.sync())

        self.listener_tasks: list[asyncio.Task] = self.create_listeners()
        self.output_task = asyncio.create_task(self.output_work())

        self.output = {}

    """
    Main interaction coroutine: Get next value out of the queue.
    """

    async def receive(self) -> dict:
        return await self.output_queue.get()

    async def sync(self) -> None:
        print("Starting sync")
        datas = await asyncio.gather(*[queue.get() for queue in self.input_queues])
        output_data = {}
        data = {}

        latest_timestamp: float = 0.0
        timestamps = []

        print("Syncing...")
        for data in datas:
            timestamps.append(data["epoch"])
            if data["epoch"] > latest_timestamp:
                latest_timestamp = data["epoch"]

                # only take the piece of the latest data
                output_data = data

        for resampler, ts in zip(self.resamplers, timestamps):
            while ts < latest_timestamp:
                data = await resampler.receive()
                ts = float(data["epoch"])

            output_data.update(data)

        print("Finished initalization")
        self.initialized.set()

    """
    Coroutine that waits for new queue data and updates dict.
    """

    async def update_dict_from_queue(self, queue):
        # queue is passed by reference, python y u so weird!
        data = await queue.get()
        if self.output and self.output["epoch"] != data["epoch"]:
            print("Oh shit, this is bad!")
        self.output.update(data)

    """
    Output worker: iterate through queues, read data and join into output queue.
    """

    async def output_work(self):
        print("Output worker waiting for intitialization")
        await self.initialized.wait()
        print("Output worker resuming")

        while True:
            self.output = {}
            tasks = [asyncio.create_task(self.update_dict_from_queue(qu)) for qu in self.input_queues]
            await asyncio.gather(*tasks)
            # for queue in self.input_queues:
            #     data = await queue.get()
            #     if self.output and self.output["epoch"] != data["epoch"]:
            #         print("Oh shit, this is bad!")
            #     self.output.update(data)
            await self.output_queue.put(self.output)

    """
    Worker: wait for new resampled data and put into assigned queue.
    """

    async def listener_task(self, resampler, queue):
        while True:
            data = await resampler.receive()
            await queue.put(data)

    """
    Link resamplers and Queues together in tasks.
    """

    def create_listeners(self) -> list[asyncio.Task]:
        tasks: list[asyncio.Task] = []
        for res, queue in zip(self.resamplers, self.input_queues):
            task = asyncio.create_task(self.listener_task(res, queue))
            tasks.append(task)

        return tasks
