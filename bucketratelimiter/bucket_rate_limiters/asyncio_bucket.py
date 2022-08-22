import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Optional, Union

from .bucket_abc import AsyncTimeRateLimiterABC, BucketTimeRateLimiterABC

AsyncFuncType = Callable[..., Union[Awaitable, Coroutine]]


class AsyncioBucketTimeRateLimiter(BucketTimeRateLimiterABC, AsyncTimeRateLimiterABC):
    def __init__(
        self,
        max_size: int = 4,
        recovery_time: float = 1.0,
        rest_time: float = 0.2,
        callback: Optional[Callable[..., Any]] = None,
    ) -> None:
        self.max_size: int = max_size
        self.active_slots: int = max_size  # number of active slots at the moment
        self.recovery_time: float = recovery_time
        self.rest_time: float = rest_time
        # used to signal "external" workers that bucket is "empty"
        self.event_bucket_empty: asyncio.Event = asyncio.Event()
        # separate asyncio task to return bucket to full size
        self.reactivate_task: Optional[asyncio.Task[Any]] = None
        self.callback: Optional[Callable[..., Any]] = callback

    def _decrement(self) -> None:
        if self.active_slots > 0:
            self.active_slots -= 1

    async def _reactivate_slots(self) -> None:
        while True:
            await asyncio.sleep(self.recovery_time)
            self.active_slots = self.max_size
            self.event_bucket_empty.set()

    async def wrap_operation(self, func: AsyncFuncType, *args: Any, **kwargs: Any) -> Any:
        while True:
            if self.event_bucket_empty.is_set():  # if bucket is not empty do work
                if self.active_slots == 0:
                    self.event_bucket_empty.clear()
                else:
                    self._decrement()
                    res = await func(*args, **kwargs)
                    if self.callback is not None:
                        self.callback()
                    return res
            else:
                await asyncio.sleep(self.rest_time)

    def activate(self) -> None:
        if self.reactivate_task is None:  # prevents creation of several activate tasks
            self.event_bucket_empty.set()  # set event flag that bucket is ready
            self.reactivate_task = asyncio.ensure_future(self._reactivate_slots())

    def deactivate(self) -> None:
        if self.reactivate_task is not None:
            if self.reactivate_task.done() is False:
                try:
                    self.reactivate_task.cancel()
                except asyncio.CancelledError:  # pragma: no cover
                    pass

    def __call__(self, f: AsyncFuncType) -> AsyncFuncType:
        @wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.activate()
            return await self.wrap_operation(f, *args, **kwargs)

        return wrapper

    async def __aenter__(self) -> "AsyncioBucketTimeRateLimiter":
        self.activate()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.deactivate()
