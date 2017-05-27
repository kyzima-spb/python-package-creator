# coding: utf-8

from os import makedirs
from os.path import (
    basename,
    join as join_path,
    exists as file_exists
)
import pickle

import __main__
from appdirs import user_cache_dir


def cached(filename):
    """Декоратор кеширует результат функции в Pickle файл."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            fullpath = user_cache_dir(basename(__main__.__file__))

            makedirs(fullpath, exist_ok=True)

            fullpath = join_path(fullpath, filename)

            if file_exists(fullpath):
                with open(fullpath, 'rb') as f:
                    return pickle.load(f)

            data = func(*args, **kwargs)

            with open(fullpath, 'wb') as f:
                pickle.dump(data, f)

            return data

        return wrapper

    return decorator
