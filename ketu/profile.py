"""Profiling module"""

from functools import wraps
from time import time


def timing(func):
    """Decorator to profile a function"""
    @wraps(func)
    def wrap(*args, **kw):
        start = time()
        result = func(*args, **kw)
        end = time()
        print(f"{func.__name__} took: {end-start}:2.4f sec\n")
        return result
    return wrap