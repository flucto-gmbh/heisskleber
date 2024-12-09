import asyncio
import json

import pytest

from heisskleber.udp import UdpConf, UdpReceiver, UdpSender


class MockUdpReceiver:
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

    async def stop(self):
        """Stop the UDP receiver."""
        if hasattr(self, "transport"):
            self.transport.close()


class MockUdpSender:
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

    async def stop(self):
        """Stop the UDP receiver."""
        if hasattr(self, "transport"):
            self.transport.close()


@pytest.mark.asyncio
async def test_udp_source() -> None:
    receiver_host = "127.0.0.1"
    receiver_port = 35699
    receiver = UdpReceiver(UdpConf(host=receiver_host, port=receiver_port))

    try:
        await receiver.start()

        sink = MockUdpSender()
        try:
            await sink.start(receiver_host, receiver_port)
            sink.transport.sendto(data=json.dumps({"message": "hi there!"}).encode())

            data, extra = await receiver.receive()
            assert data == {"message": "hi there!"}
        finally:
            await sink.stop()
    finally:
        await receiver.stop()


@pytest.mark.asyncio
async def test_actual_udp_transport():
    """Test actual UDP communication between sender and receiver."""
    mock_receiver = MockUdpReceiver()
    receiver_host = "127.0.0.1"
    receiver_port = 45678

    try:
        await mock_receiver.start(receiver_host, receiver_port)

        config = UdpConf(host=receiver_host, port=receiver_port)
        sink = UdpSender(config)

        try:
            await sink.start()

            test_data = {"message": "Hello, UDP!"}
            await sink.send(test_data)
            await asyncio.sleep(0.1)

            assert len(mock_receiver.received_data) == 1
            received_bytes = mock_receiver.received_data[0]
            assert b'"message": "Hello, UDP!"' in received_bytes

        finally:
            await sink.stop()

    finally:
        await mock_receiver.stop()
