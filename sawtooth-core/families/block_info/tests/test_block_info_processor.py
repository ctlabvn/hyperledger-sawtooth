import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sawtooth_block_info.processor.main import create_console_handler


def test_create_console_handler0(benchmark):
    # benchmark something
    result = benchmark(create_console_handler, 0)
    return


def test_create_console_handler1(benchmark):
    # benchmark something
    result = benchmark(create_console_handler, 1)
    return


def test_create_console_handlerN(benchmark):
    # benchmark something
    result = benchmark(create_console_handler, 99)
    return
