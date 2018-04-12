from sawtooth_ias_proxy.utils import LruCache

cache = LruCache(200)
cache["key"] = "value"


def test_set_lru_cache(benchmark):
    result = benchmark(cache.__setitem__, "123", "abc")
    return


def test_get_lru_cache(benchmark):
    result = benchmark(cache.get, "key")
    return
