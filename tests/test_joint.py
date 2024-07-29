from unittest.mock import AsyncMock, MagicMock

import pytest

from heisskleber.mqtt import MqttSource
from heisskleber.stream import Joint, Resampler, ResamplerConf


@pytest.fixture
def mock_subscriber():
    return MagicMock()


class EndofData(Exception):
    pass


@pytest.mark.asyncio
async def test_two_streams_are_parallel():
    """
    Test that Joint can synchronize two streams that start at different epoch values.

    The setup includes the mocked subscribers async receive() and run() methods.
    """
    sub1 = MagicMock(autospec=MqttSource)
    sub1.receive.side_effect = AsyncMock(
        side_effect=[
            ("topic1", {"epoch": 0, "x": 0}),
            ("topic1", {"epoch": 1, "x": 1}),
            ("topic1", {"epoch": 2, "x": 2}),
            ("topic1", {"epoch": 3, "x": 3}),
            ("topic1", {"epoch": 4, "x": 4}),
            ("topic1", {"epoch": 5, "x": 5}),
            ("topic1", {"epoch": 6, "x": 6}),
            EndofData(),
        ]
    )
    sub1.run = AsyncMock()
    sub2 = MagicMock(autospec=MqttSource)
    sub2.run = AsyncMock()
    sub2.receive.side_effect = AsyncMock(
        side_effect=[
            ("topic2", {"epoch": 2, "y": 0}),
            ("topic2", {"epoch": 3, "y": 1}),
            ("topic2", {"epoch": 4, "y": 2}),
            ("topic2", {"epoch": 5, "y": 3}),
            ("topic1", {"epoch": 6, "x": 6}),
            ("topic1", {"epoch": 7, "x": 7}),
            ("topic1", {"epoch": 8, "x": 8}),
            EndofData(),
        ]
    )
    conf = ResamplerConf(resample_rate=1000)

    resamplers = [Resampler(conf, sub1), Resampler(conf, sub2)]

    joiner = Joint(conf, resamplers)

    return_data = await joiner.receive()
    assert return_data == {"epoch": 2, "x": 2, "y": 0}

    return_data = await joiner.receive()
    assert return_data == {"epoch": 3, "x": 3, "y": 1}
