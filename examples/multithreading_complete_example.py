from threading import Thread
from queue import Queue
from typing import NamedTuple
from datetime import datetime
import time
from functools import partial

from bucketratelimiter import MThreadedBucketTimeRateLimiter


TASKS_TO_COMPLETE = [(i, i, i) for i in range(20)]
WORKER_NUM = 30


class TestResult(NamedTuple):
    res: int
    start: str
    end: str


def some_callback(x: int, y: int, z: int) -> None:
    """This is some callback function"""
    print(f"Callback result: {x + y + z}")


LIMITER = MThreadedBucketTimeRateLimiter(callback=partial(some_callback, 1, 2, 3))  # declare rate limiter here


@LIMITER  # use limiter as a decorator to rate limit some_func
def some_func(x: int, y: int, z: int, *, time_to_complete: float = 1) -> TestResult:
    """Imagine it is a fetch function and we would like to implement rate limiter to it."""
    format_time = "%H:%M:%S"
    start = datetime.utcnow().strftime(format_time)
    time.sleep(time_to_complete)
    end = datetime.utcnow().strftime(format_time)
    result = x + y + z - z - y  # = x

    return TestResult(result, start, end)


def worker(q: Queue) -> None:
    """Workers which do some stuff."""
    while True:
        item = q.get()
        res = some_func(*item)
        print(f"Result: {res.res} | {res.start} - {res.end}")
        q.task_done()


def main_entry_point() -> None:
    """Main entry point of our multithreading app."""
    q = Queue()
    for task in TASKS_TO_COMPLETE:
        q.put(task)

    # use LIMITER as context manager to ensure its correct activation and end of work
    with LIMITER:
        for _ in range(1, WORKER_NUM + 1):
            Thread(target=worker, args=(q, ), daemon=True).start()

        q.join()


if __name__ == '__main__':
    start_t = time.monotonic()
    main_entry_point()
    print(f"Time passed: {time.monotonic() - start_t}")
