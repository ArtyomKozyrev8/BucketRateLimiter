[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![UNITTESTS](https://github.com/ArtyomKozyrev8/BucketRateLimiter/actions/workflows/unittests.yml/badge.svg)](https://github.com/ArtyomKozyrev8/BucketRateLimiter/actions/workflows/unittests.yml)
[![codecov](https://codecov.io/gh/ArtyomKozyrev8/BucketRateLimiter/branch/main/graph/badge.svg?token=7LHFJ0UJYQ)](https://codecov.io/gh/ArtyomKozyrev8/BucketRateLimiter)
[![MyPy](https://github.com/ArtyomKozyrev8/BucketRateLimiter/actions/workflows/mypy.yml/badge.svg)](https://github.com/ArtyomKozyrev8/BucketRateLimiter/actions/workflows/mypy.yml)

# BucketRateLimiter

**bucketratelimiter** is the collection of rate limiters, which are based on **Bucket** conception.


### How to install:

`pip install bucketratelimiter`

### Examples:

You can find complete examples on how to use `AsyncioBucketTimeRateLimiter` and `MThreadedBucketTimeRateLimiter` in
folder **examples** of this repository. Also you can check **tests** folder and get some tricks from unittests.

### How to use:

##### Create rate limiter:

```python
from bucketratelimiter import AsyncioBucketTimeRateLimiter

# max_size = 4 and recovery_time = 1.0
# means that we would like to limit something to 4 attempts per second
# max_size - is a size of internal bucket
# recovery_time - time to make bucket full again
# rest_time - is the time to sleep for workers which can not proceed further due to rate limiter
# callback - is a function which should be called after task will be completed
ASYNC_LIMITER = AsyncioBucketTimeRateLimiter(
    max_size=4,
    recovery_time=1.0,
    rest_time=0.2,
    callback=None,
)
``` 

```python
from bucketratelimiter import MThreadedBucketTimeRateLimiter

ASYNC_LIMITER = MThreadedBucketTimeRateLimiter(
    max_size=4,
    recovery_time=1.0,
    rest_time=0.2,
    callback=None,
)
``` 

##### "Wrap" some function in ratelimiter:

```python
import asyncio
from bucketratelimiter import AsyncioBucketTimeRateLimiter

limiter = AsyncioBucketTimeRateLimiter()

@limiter # we use decorator to limit the function to a certain number of attempts per second
async def some_func_to_limit(sleep_time: float = 1.0) -> None:
    await asyncio.sleep(sleep_time)
```


```python
import time
from bucketratelimiter import MThreadedBucketTimeRateLimiter

limiter = MThreadedBucketTimeRateLimiter()

@limiter # we use decorator to limit the function to a certain number of attempts per second
def some_func_to_limit(sleep_time: float = 1.0) -> None:
    time.sleep(sleep_time)
```

##### Activate ratelimiter logic:

```python
limiter = AsyncioBucketTimeRateLimiter()

async def main_entry_point() -> None:
    """Main entry point of our asyncio app."""
    q = asyncio.Queue()
    for task in TASKS_TO_COMPLETE:
        await q.put(task)

    # use LIMITER as context manager to ensure its correct activation and end of work
    async with limiter:
        for w in [worker(q) for _ in range(1, WORKER_NUM + 1)]:
            asyncio.create_task(w)

        await q.join()
```

```python
limiter = MThreadedBucketTimeRateLimiter()

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
```

### HOW TO USE LOW LEVEL API:

##### Use without context manager:

```python
# Use RateLimiter's method to activate and deactivate it's inner logic
# instead of using context managers
try:
    limiter.activate()
finally:
    limiter.deactivate()
```

##### Use without functions decoration:

```python
import asyncio
from bucketratelimiter import AsyncioBucketTimeRateLimiter

limiter = AsyncioBucketTimeRateLimiter()

async def some_func_to_limit(sleep_time: float = 1.0) -> None:
    await asyncio.sleep(sleep_time)
...
async with limiter:
    await limiter.wrap_operation(some_func_to_limit, sleep_time=1.0)

# ATTENTION !
# Do not use wrap_operation to some function more than once
# Do not apply decorator to some function if you use wrap_operation
# It can lead to unexpected results
```

```python
import time
from bucketratelimiter import MThreadedBucketTimeRateLimiter

limiter = MThreadedBucketTimeRateLimiter()

def some_func_to_limit(sleep_time: float = 1.0) -> None:
    time.sleep(sleep_time)
...
with limiter:
    limiter.wrap_operation(some_func_to_limit, sleep_time=1.0)
```

### FOR CONTRIBUTORS:

Clone the project:
```commandline
https://github.com/ArtyomKozyrev8/BucketRateLimiter.git
cd BucketRateLimiter
```
Create a new virtualenv:
```commandline
python3 -m venv env
source env/bin/activate
```
Install all requirements:
```commandline
pip install -e '.[develop]'
```

**Run Tests:**


```commandline
mypy --strict bucketratelimiter

pytest --cov=bucketratelimiter tests/

coverage report

coverage html
```
