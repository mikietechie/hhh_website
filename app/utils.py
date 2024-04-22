import typing
from django.core.cache import cache


def get_cached(key: str, get_default:typing.Callable=None, timeout:int=None):
    value = cache.get(key)
    if (not value) and get_default:
        value = get_default()
        cache.set(key, value, timeout)
    return value
