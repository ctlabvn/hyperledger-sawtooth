import time

def test_timer(benchmark):
    # benchmark something
    result = benchmark(time.sleep, 0.000001)
