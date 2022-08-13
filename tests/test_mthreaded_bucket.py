from queue import Queue
from typing import NamedTuple
from time import sleep, monotonic
from threading import Thread

from bucketratelimiter import MThreadedBucketTimeRateLimiter


def test__decrement():
    bucket = MThreadedBucketTimeRateLimiter(max_size=4)
    for i in range(10):
        bucket._decrement()


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


def worker(q: Queue, func: MThreadedBucketTimeRateLimiter, sleep_time: float = 1.0) -> None:
    while True:
        q.get()
        func(sleep_time)
        q.task_done()


def main_entry_point(env_params: EnvironmentParams, broken_reactivate_task: bool = False) -> int:
    """Main entry point of our asyncio tests."""
    e = env_params

    callback = None
    if e.use_callback_func:
        callback = callback_func

    bucket = MThreadedBucketTimeRateLimiter(
        max_size=e.max_bucket_size,
        recovery_time=e.recovery_time,
        callback=callback,
    )

    @bucket
    def some_func_to_limit(sleep_time: float = 1.0) -> None:
        sleep(sleep_time)
        return

    start = monotonic()
    q = Queue()
    for task in range(e.tasks_number):
        q.put(task)  # send all tasks to the Queue

    with bucket:
        for w in range(e.workers_number):
            Thread(target=worker, args=(q, some_func_to_limit, e.time_to_finish_one_task, ), daemon=True).start()

        q.join()  # wait until all task in queue were done

        if broken_reactivate_task:
            bucket.event_full_stop.clear()
            bucket.reactivate_task = None

    return int(monotonic() - start)


def test_wrapper_main_entry_point_1():
    e = EnvironmentParams(
        max_bucket_size=4,
        recovery_time=1.0,
        use_callback_func=True,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=5,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_2():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=2,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_3():
    e = EnvironmentParams(
        max_bucket_size=2,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=10,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_4():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=1.0,
        expected_finish_time=2,
    )
    res = main_entry_point(e, broken_reactivate_task=True)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_5():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=60,
        time_to_finish_one_task=1.0,
        expected_finish_time=6,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_6():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=2.0,
        expected_finish_time=3,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_7():
    e = EnvironmentParams(
        max_bucket_size=10,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=5.0,
        expected_finish_time=6,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res


def test_wrapper_main_entry_point_8():
    e = EnvironmentParams(
        max_bucket_size=5,
        recovery_time=1.0,
        use_callback_func=False,
        workers_number=30,
        tasks_number=20,
        time_to_finish_one_task=5.0,
        expected_finish_time=8,
    )
    res = main_entry_point(e)
    assert e.expected_finish_time == res
