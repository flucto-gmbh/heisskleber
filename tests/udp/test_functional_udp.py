import asyncio
import json

import pytest
from heisskleber.udp import UdpConf, UdpSink, UdpSource


class UdpReceiver:
    """Helper class to receive UDP messages for testing."""

    transport: asyncio.DatagramTransport
    protocol: asyncio.DatagramProtocol

    def __init__(self):
        self.received_data = []

    class ReceiverProtocol(asyncio.DatagramProtocol):
        def __init__(self, received_data):
            self.received_data = received_data

        def connection_made(self, transport):
            pass

        def datagram_received(self, data, addr):
            self.received_data.append(data)

    async def start(self, host: str, port: int):
        """Start the UDP receiver."""
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: self.ReceiverProtocol(self.received_data),
            local_addr=(host, port),
        )

    def stop(self):
        """Stop the UDP receiver."""
        if hasattr(self, "transport"):
            self.transport.close()


class UdpSender:
    """Helper class to send UDP messages for testing."""

    transport: asyncio.DatagramTransport
    protocol: asyncio.DatagramProtocol

    def __init__(self):
        self.received_data = []

    class SenderProtocol(asyncio.DatagramProtocol):
        def connection_made(self, transport):
            pass

    async def start(self, host: str, port: int):
        """Start the UDP receiver."""
        loop = asyncio.get_running_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: self.SenderProtocol(),
            remote_addr=(host, port),
        )

    def stop(self):
        """Stop the UDP receiver."""
        if hasattr(self, "transport"):
            self.transport.close()


@pytest.mark.asyncio()
async def test_udp_source() -> None:
    receiver_host = "127.0.0.1"
    receiver_port = 35699
    receiver = UdpSource(UdpConf(host=receiver_host, port=receiver_port))

    try:
        await receiver.start()

        sender = UdpSender()
        try:
            await sender.start(receiver_host, receiver_port)
            sender.transport.sendto(data=json.dumps({"message": "hi there!"}).encode())

            data, extra = await receiver.receive()
            assert data == {"message": "hi there!"}
        finally:
            sender.stop()
    finally:
        receiver.stop()


@pytest.mark.asyncio()
async def test_actual_udp_transport():
    """Test actual UDP communication between sender and receiver."""
    receiver = UdpReceiver()
    receiver_host = "127.0.0.1"
    receiver_port = 45678

    try:
        await receiver.start(receiver_host, receiver_port)

        config = UdpConf(host=receiver_host, port=receiver_port)
        sink = UdpSink(config)

        try:
            await sink.start()

            test_data = {"message": "Hello, UDP!"}
            await sink.send(test_data)
            await asyncio.sleep(0.1)

            assert len(receiver.received_data) == 1
            received_bytes = receiver.received_data[0]
            assert b'"message": "Hello, UDP!"' in received_bytes

        finally:
            sink.stop()

    finally:
        receiver.stop()
