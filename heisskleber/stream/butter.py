from collections import deque
from typing import Any

import numpy as np
import scipy.signal  # type: ignore [import-untyped]
from numpy.typing import NDArray

from heisskleber.core import AsyncSource
from heisskleber.stream.filter import Filter


class LiveLFilter:
    """
    Filter using standard difference equations.
    Kudos to Sam Proell https://www.samproell.io/posts/yarppg/yarppg-live-digital-filter/
    """

    def __init__(self, b: NDArray[np.float64], a: NDArray[np.float64], init_val: float = 0.0) -> None:
        """Initialize live filter based on difference equation.

        Args:
            b (array-like): numerator coefficients obtained from scipy.
            a (array-like): denominator coefficients obtained from scipy.
        """
        self.b = b
        self.a = a
        self._xs = deque([init_val] * len(b), maxlen=len(b))
        self._ys = deque([init_val] * (len(a) - 1), maxlen=len(a) - 1)

    def __call__(self, x: float) -> float:
        """Filter incoming data with standard difference equations."""
        self._xs.appendleft(x)
        y = np.dot(self.b, self._xs) - np.dot(self.a[1:], self._ys)
        y = y / self.a[0]
        self._ys.appendleft(y)

        return y  # type: ignore [no-any-return]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(b={self.b}, a={self.a})"


class ButterFilter(Filter):
    """
    Butterworth filter based on scipy.

    Args:
        source (AsyncSource): Source of data.
        cutoff_freq (float): Cutoff frequency.
        sampling_rate (float): Sampling rate of the input signal, i.e update frequency
        btype (str): Type of filter, "high" or "low"
        order (int): order of the filter to be applied

    Example:
        >>> source = get_async_source()
        >>> filter = LowPassFilter(source, 0.1, 100, 3)
        >>> async for topic, data in filter:
        >>>     print(topic, data)
    """

    def __init__(
        self, source: AsyncSource, cutoff_freq: float, sampling_rate: float, btype: str = "low", order: int = 3
    ) -> None:
        self.source = source
        nyquist_fq = sampling_rate / 2
        Wn = cutoff_freq / nyquist_fq
        self.b, self.a = scipy.signal.iirfilter(order, Wn=Wn, fs=sampling_rate, btype=btype, ftype="butter")
        self.filters: dict[str, LiveLFilter] = {}

    def _filter(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self.filters:
            for key in data:
                self.filters[key] = LiveLFilter(a=self.a, b=self.b)

        for key, value in data.items():
            data[key] = self.filters[key](value)

        return data
