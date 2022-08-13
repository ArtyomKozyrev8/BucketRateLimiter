from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class BucketTimeRateLimiterABC(ABC):
    @abstractmethod
    def __init__(
        self,
        max_size: int,
        recovery_time: float,
        rest_time: float,
        callback: Optional[Callable[..., Any]],
    ) -> None:
        """
        BucketRateLimiter is used to limit number of "simultaneous" operations to the specified number.
        e.g. some external API allows you to make only 4 requests per second.
        BucketRateLimiter can help to achieve the goal.
        :param max_size: max size of Bucket. Should be positive integer number.
        This is the maximum number of operations (e.g. requests) you can launch in the provided time
        interval (recovery_time).
        e.g. API allows you to make 4 requests per second, hereby recovery_time = 4
        :param recovery_time: time in seconds to recover Bucket to full size.
        e.g. API allows to make 4 requests per second, hereby recovery_time = 1.0
        :param rest_time: time to give "workers" who use bucket to sleep if bucket is empty at the moment.
        BucketRateLimiter deliberately does not use any internal pool of workers to make
        it responsibility of user how to implement "workers"
        :param callback: not "awaitable" function which is called when any of workers have finished task.
        """
        ...

    @abstractmethod
    def _decrement(self) -> None:
        """Decrements internal counter self.active_slots by one."""
        ...

    @abstractmethod
    def activate(self) -> None:
        """The method "activates" BucketRateLimiter internal logic."""
        ...

    @abstractmethod
    def deactivate(self) -> None:
        """The method stops self.reactivate_task operations."""
        ...

    @abstractmethod
    def __call__(self, f: Any) -> Any:
        """The method is created in order to use BucketRateLimiter instance as decorator."""
        ...


class AsyncTimeRateLimiterABC(ABC):
    @abstractmethod
    async def _reactivate_slots(self) -> None:
        """Every n seconds (self.recovery_time) refresh number of self.active_slots to max number."""
        ...

    @abstractmethod
    async def wrap_operation(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper around some async function which is used in "workers".
        It limits number of attempts to a certain maximum number.
        :param func: async function we would like to limit.
        :param args: this async function args.
        :param kwargs: this async function kwargs.
        :return: returns the same result as func is supposed to return.
        """
        ...

    @abstractmethod
    async def __aenter__(self) -> Any:
        """Implemented to use the BucketRateLimiter instance as context manager."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Implemented to use the BucketRateLimiter instance as context manager."""
        ...


class MThreadedBucketTimeRateLimiterABC(ABC):
    @abstractmethod
    def _reactivate_slots(self) -> None:
        """Every n seconds (self.recovery_time) refresh number of self.active_slots to max number."""
        ...

    @abstractmethod
    def wrap_operation(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper around some sync function which is used in "workers".
        It limits number of attempts to a certain maximum number.
        :param func: some sync function we would like to apply rate limit to.
        :param args: the sync function args.
        :param kwargs: the sync function kwargs.
        :return: returns the same result as the func is supposed to return.
        """
        ...

    @abstractmethod
    def __enter__(self) -> Any:
        """Implemented to use the BucketRateLimiter instance as context manager."""
        ...

    @abstractmethod
    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Implemented to use the BucketRateLimiter instance as context manager."""
        ...
