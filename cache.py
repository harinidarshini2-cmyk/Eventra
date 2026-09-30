import time

cache = {}

CACHE_DURATION = 60


def get_cache(key):
    if key in cache:
        value, timestamp = cache[key]

        if time.time() - timestamp < CACHE_DURATION:
            print(f"[CACHE] HIT: {key}")
            return value

        del cache[key]

    print(f"[CACHE] MISS: {key}")
    return None


def set_cache(key, value):
    cache[key] = (value, time.time())
    print(f"[CACHE] SET: {key}")