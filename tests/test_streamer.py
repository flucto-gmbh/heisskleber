import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from heisskleber.mqtt import AsyncMqttSubscriber
from heisskleber.stream import Resampler, ResamplerConf


class EndofData(Exception):
    pass


# Mocking the MQTT Subscriber
@pytest.fixture
def mock_subscriber():
    mock = MagicMock(spec=AsyncMqttSubscriber)
    mock.receive = AsyncMock(
        side_effect=[
            ("topic1", {"epoch": 1609459200, "data": 1}),  # First message
            ("topic1", {"epoch": 1609459201, "data": 2}),  # Second message
            ("topic1", {"epoch": 1609459202, "data": 3}),  # Second message
            ("topic1", {"epoch": 1609459203, "data": 4}),  # Second message
            ("topic1", {"epoch": 1609459204, "data": 5}),  # Second message
            ("end", {"epoch": 1609459205, "data": 6}),  # Second message
        ]
    )
    return mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "resample_rate,expected_length", [(1_000, 5), (2_000, 3), (500, 10)]
)
async def test_resampler(mock_subscriber, resample_rate, expected_length):
    config = ResamplerConf(
        resample_rate=resample_rate
    )  # Fill in your MQTT configuration
    resampler = Resampler(config, mock_subscriber)

    # Start the resampler run loop in a background task
    _ = asyncio.create_task(resampler.run())

    print(
        f"Running test at {resample_rate / 1_000} Hz, expecting {expected_length} data points"
    )
    print("=======================================================================")

    # Test the resample method
    resampled_data = []
    async for data in resampler.resample():
        print(f"resampled data: {data}")
        resampled_data.append(data)
        if resampler.buffer.qsize() == 0:
            break
    print("=======================================================================")
    print("\n")

    assert len(resampled_data)
