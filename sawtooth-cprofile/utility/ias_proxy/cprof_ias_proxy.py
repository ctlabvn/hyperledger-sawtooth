import cProfile
from sawtooth_ias_proxy.utils import LruCache

cache = LruCache(200)
cache["key"] = "value"

if __name__ == '__main__':
    print("\n====== cProfile: ./utility/ias_proxy/cprof_ias_proxy.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    cache.__setitem__(key="123", value="abc")
    cache.get(key="key")
    
    pr.disable()
    pr.print_stats(sort='time')

