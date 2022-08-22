import asyncio
from time import monotonic
from typing import NamedTuple, Callable, Union, Awaitable, Coroutine

import pytest

from bucketratelimiter import AsyncioBucketTimeRateLimiter


AsyncFuncType = Callable[..., Union[Awaitable, Coroutine]]


class EnvironmentParams(NamedTuple):
    max_bucket_size: int
    recovery_time: float
    use_callback_func: bool
    workers_number: int
    tasks_number: int
    time_to_finish_one_task: float
    expected_finish_time: int


def callback_func() -> None:
    return


async def worker(q: asyncio.Queue, func: AsyncioBucketTimeRateLimiter, sleep_time: float = 1.0) -> None:
    while True:
        await q.get()
        await func(sleep_time)
        q.task_done()


async def main_entry_point(env_params: EnvironmentParams, broken_reactivate_task: bool = False) -> int:
    """Main entry point of our asyncio tests."""
    e = env_params

    callback = None
    if e.use_callback_func:
        callback = callback_func

    bucket = AsyncioBucketTimeRateLimiter(max_size=e.max_bucket_size, recovery_time=e.recovery_time, callback=callback)

    @bucket
    async def some_func_to_limit(sleep_time: float = 1.0) -> None:
        await asyncio.sleep(sleep_time)
        return

    start = monotonic()
    print(start)
    q = asyncio.Queue()
    for task in range(e.tasks_number):
        await q.put(task)  # send all tasks to the Queue

    asyncio_tasks_to_cancel = []
    async with bucket:
        for w in [
            worker(q, some_func_to_limit, e.time_to_finish_one_task) for _ in range(e.workers_number)
        ]:
            asyncio_tasks_to_cancel.append(asyncio.ensure_future(w))

        await q.join()  # wait until all task in queue were done
        if broken_reactivate_task:
            bucket.reactivate_task = None

    [i.cancel() for i in asyncio_tasks_to_cancel]
    return int(monotonic() - start)


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_1():
    e = EnvironmentParams(
        max_bucket_size=4,
        recovery_time=1.0,
        use_callback_func=True,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=5,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_2():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=2,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_3():
    e = EnvironmentParams(
        max_bucket_size=2,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=10,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_4():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=2,
    )
    res = await main_entry_point(e, broken_reactivate_task=True)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_5():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=60,
        time_to_finish_one_task=1.0,
        expected_finish_time=6,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_6():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=2.0,
        expected_finish_time=3,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_7():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=5.0,
        expected_finish_time=6,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


@pytest.mark.asyncio
async def test_wrapper_main_entry_point_8():
    e = EnvironmentParams(
        max_bucket_size=5,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=5.0,
        expected_finish_time=8,
    )
    res = await main_entry_point(e)
    assert e.expected_finish_time == res


def test__decrement():
    bucket = AsyncioBucketTimeRateLimiter(max_size=1)
    for i in range(10):
        bucket._decrement()
