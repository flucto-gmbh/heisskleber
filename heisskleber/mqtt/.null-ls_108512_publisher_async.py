from __future__ import annotations

import asyncio
from typing import Any

import aiomqtt

from heisskleber.core.packer import get_packer
from heisskleber.core.types import AsyncSink

from .config import MqttConf


class AsyncMqttPublisher(AsyncSink):
    """
    MQTT publisher class.
    Can be used everywhere that a flucto style publishing connection is required.

    Network message loop is handled in a separated thread.
    """

    def __init__(self, config: MqttConf) -> None:
        self.config = config
        self.pack = get_packer(config.packstyle)
        self._send_queue = asyncio.Queue()
        self._sender_task = asyncio.create_task(self.send_work())

    async def send(self, data: dict[str, Any], topic: str) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """

        await self._send_queue.put((data, topic))

    async def send_work(self) -> None:
        """
        Takes python dictionary, serializes it according to the packstyle
        and sends it to the broker.

        Publishing is asynchronous
        """
        async with aiomqtt.Client(
            hostname=self.config.broker, port=self.config.port, username=self.config.user, password=self.config.password
        ) as client:
            while True:
                data, topic = await self._send_queue.get()
                payload = self.pack(data)
                await client.publish(topic, payload)
