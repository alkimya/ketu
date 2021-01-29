from functools import wraps
from time import time


def time_it(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = time() * 1000
        try:
            return func(*args, **kwargs)
        finally:
            stop = time() * 1000 - start
            print(f"\nTotal execution time: {stop} ms")

    return _time_it
