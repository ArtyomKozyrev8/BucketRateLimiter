import threading as th
from functools import wraps
from time import sleep
from typing import Any, Callable, Optional

from .bucket_abc import BucketTimeRateLimiterABC, MThreadedBucketTimeRateLimiterABC


class MThreadedBucketTimeRateLimiter(BucketTimeRateLimiterABC, MThreadedBucketTimeRateLimiterABC):
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
        self.event_bucket_empty: th.Event = th.Event()
        # separate asyncio task to return bucket to full size
        self.reactivate_task: Optional[th.Thread] = None
        self.callback: Optional[Callable[..., Any]] = callback
        self.sync_lock = th.Lock()
        self.event_full_stop = th.Event()

    def _decrement(self) -> None:
        with self.sync_lock:
            if self.active_slots > 0:
                self.active_slots -= 1

    def _reactivate_slots(self) -> None:
        while self.event_full_stop.is_set():
            sleep(self.recovery_time)
            with self.sync_lock:
                self.active_slots = self.max_size
                self.event_bucket_empty.set()

    def wrap_operation(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        while True:
            if self.event_bucket_empty.is_set():  # if bucket is not empty do work
                if self.active_slots == 0:
                    self.event_bucket_empty.clear()
                else:
                    self._decrement()
                    res = func(*args, **kwargs)
                    if self.callback is not None:
                        self.callback()
                    return res
            else:
                sleep(self.rest_time)

    def activate(self) -> None:
        if self.reactivate_task is None:  # prevents creation of several activate tasks
            self.event_full_stop.set()  # prepare full stop event
            self.event_bucket_empty.set()  # set event flag that bucket is ready
            self.reactivate_task = th.Thread(target=self._reactivate_slots, daemon=True)
            self.reactivate_task.start()

    def deactivate(self) -> None:
        if self.reactivate_task is not None:
            self.event_full_stop.clear()

    def __call__(self, f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.activate()
            return self.wrap_operation(f, *args, **kwargs)

        return wrapper

    def __enter__(self) -> "MThreadedBucketTimeRateLimiter":
        self.activate()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.deactivate()
