import asyncio
from collections.abc import Coroutine
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def retry(
    every: int = 5,
    strategy: str = "always",
    catch: type[Exception] | tuple[type[Exception], ...] = Exception,
    logger_fn: Callable[[str, dict[str, Any]], None] | None = None,
) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
    """Retry a coroutine."""

    def decorator(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            retries = 0
            while True:
                try:
                    result = await func(*args, **kwargs)
                    break
                except catch as e:
                    if logger_fn:
                        logger_fn(
                            "Error occurred: %(err). Retrying in %(seconds) seconds",
                            {"err": e, "seconds": every},
                        )
                    retries += 1
                    await asyncio.sleep(every)
                except asyncio.CancelledError:
                    raise

                if strategy != "always":
                    raise NotImplementedError

            return result

        return wrapper

    return decorator
