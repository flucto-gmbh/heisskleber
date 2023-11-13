from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from heisskleber.mqtt import AsyncMqttSubscriber
from heisskleber.stream import Resampler, ResamplerConf
from heisskleber.stream.resampler import floor_dt, timestamp_generator


class EndofData(Exception):
    pass


# Mocking the MQTT Subscriber
@pytest.fixture
def mock_subscriber():
    mock = MagicMock(spec=AsyncMqttSubscriber)
    return mock


@pytest.mark.parametrize(
    "time_in,expected",
    [
        (datetime.fromtimestamp(0.1), datetime.fromtimestamp(0.0)),
        (datetime.fromtimestamp(0.6), datetime.fromtimestamp(0.5)),
        (datetime.fromtimestamp(0.9), datetime.fromtimestamp(0.5)),
        (datetime.fromtimestamp(1.1), datetime.fromtimestamp(1.0)),
    ],
)
def test_round_dt(time_in, expected):
    delta_t = timedelta(milliseconds=500)
    assert floor_dt(time_in, delta_t) == expected


@pytest.mark.parametrize(
    "start,frequency,expected",
    [
        (0.1, 500, [0.25, 0.75, 1.25]),
        (0.6, 1000, [0.5, 1.5, 2.5]),
        (0.9, 2000, [1.0, 3.0, 5.0]),
        (0.04, 50, [0.025, 0.075, 0.125]),
    ],
)
def test_timestamp_generator(start, frequency, expected):
    """Test the timestamp generator.
    Expectation is that it will generate timestamps with the frequency as stride length and
    start at the floow value of the start timestamp with half the stride length offset.
    """
    generator = timestamp_generator(start, frequency)
    for ts, exp in zip(generator, expected):
        assert ts == exp


@pytest.mark.asyncio
async def test_resampler_multiple_modes(mock_subscriber):
    mock_subscriber.receive = AsyncMock(
        side_effect=[
            ("topic1", {"epoch": 0.05, "data": 1}),  # 1st interval
            ("topic1", {"epoch": 0.10, "data": 2}),  # 1st interval
            ("topic1", {"epoch": 0.90, "data": 3}),  # 2nd inverval
            ("topic1", {"epoch": 1.10, "data": 4}),  # 2nd interval
            ("topic1", {"epoch": 1.51, "data": 6}),  # 3rd interval
            ("topic1", {"epoch": 2.51, "data": 7}),  # 4th interval
            ("topic1", {"epoch": 4.00, "data": 10}),  # 5th interval
            EndofData(),
        ]
    )

    config = ResamplerConf(resample_rate=1000)  # Fill in your MQTT configuration
    resampler = Resampler(config, mock_subscriber)

    # Test the resample method
    resampled_data = []

    with pytest.raises(EndofData):
        async for data in resampler.resample():
            resampled_data.append(data)

    assert resampled_data[0] == {"epoch": 0.0, "data": 1.5}
    assert resampled_data[1] == {"epoch": 1.0, "data": 3.5}
    assert resampled_data[2] == {"epoch": 2.0, "data": 6}


@pytest.mark.asyncio
async def test_resampler_upsampling(mock_subscriber):
    mock_subscriber.receive = AsyncMock(
        side_effect=[
            ("topic1", {"epoch": 0.0, "data": 1}),  # 1st interval
            ("topic1", {"epoch": 1.0, "data": 2}),  # 2st interval
            ("topic1", {"epoch": 2.0, "data": 3}),  # 3nd inverval
            EndofData(),
        ]
    )

    config = ResamplerConf(resample_rate=250)  # Fill in your MQTT configuration
    resampler = Resampler(config, mock_subscriber)

    resampled_data = []
    with pytest.raises(EndofData):
        async for data in resampler.resample():
            resampled_data.append(data)

    assert resampled_data[0] == {"epoch": 0.0, "data": 1.0}
    assert resampled_data[1] == {"epoch": 0.25, "data": 1.25}
    assert resampled_data[2] == {"epoch": 0.5, "data": 1.5}
    assert resampled_data[3] == {"epoch": 0.75, "data": 1.75}
    assert resampled_data[4] == {"epoch": 1.0, "data": 2.0}
    assert resampled_data[5] == {"epoch": 1.25, "data": 2.25}
