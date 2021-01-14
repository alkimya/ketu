from functools import wraps
from time import time


def time_it(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = time() * 1000
        try:
            return func(*args, **kwargs)
        finally:
            end_ = time() * 1000 - start
            print(f"\nTotal execution time: {end_ if end_ > 0 else 0} ms")

    return _time_it
