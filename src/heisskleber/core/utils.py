import asyncio
from collections.abc import Awaitable
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    retry_interval: float = 5.0,
    max_retries: int | None = None,
    exception_type: type[Exception] | tuple[type[Exception], ...] = Exception,
    logger_fn: Callable[[str, dict[str, Any]], None] | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Retry a coroutine."""

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            retries = 0
            while max_retries is None or retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except exception_type as e:  # noqa: PERF203
                    if logger_fn:
                        logger_fn(
                            "Error occurred: %(err). Retrying in %(seconds) seconds",
                            {"err": e, "seconds": retry_interval},
                        )
                    retries += 1
                    await asyncio.sleep(retry_interval)
            msg = f"Max retries ({max_retries}) exceeded"
            raise RuntimeError(msg)

        return wrapper

    return decorator
