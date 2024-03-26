from heisskleber.core.types import AsyncSource
from heisskleber.stream.filter import Filter


class GhFilter(Filter):
    """
    G-H filter (also called alpha-beta, f-g filter), simplified observer for estimation and data smoothing.

    Args:
        source (AsyncSource): Source of data.
        g (float): Correction gain for value
        h (float): Correction gain for derivative

    Example:
        >>> source = get_async_source()
        >>> filter = LowPassFilter(source, 0.1, 100, 3)
        >>> async for topic, data in filter:
        >>>     print(topic, data)
    """

    def __init__(self, source: AsyncSource, g: float, h: float):
        self.source = source
        if not 0 < g < 1.0 or not 0 < h < 1.0:
            msg = "g and h must be between 0 and 1.0"
            raise ValueError(msg)
        self.g = g
        self.h = h
        self.x: dict[str, float] = {}
        self.dx: dict[str, float] = {}

    def _filter(self, data: dict[str, float]) -> dict[str, float]:
        if not self.x:
            self.x = data
            self.dx = {key: 0.0 for key in data}
            return data

        invalid_keys = []
        ts = data.pop("epoch")
        dt = ts - self.x["epoch"]
        if abs(dt) <= 1e-4:
            data["epoch"] = ts
            return data

        for key in data:
            if not isinstance(data[key], float):
                invalid_keys.append(key)
                continue
            x_pred = self.x[key] + dt * self.dx[key]
            residual = data[key] - x_pred
            self.dx[key] = self.dx[key] + self.h * residual / dt
            self.x[key] = x_pred + self.g * residual

        for key in invalid_keys:
            self.x[key] = data[key]
        self.x["epoch"] = ts
        return self.x
