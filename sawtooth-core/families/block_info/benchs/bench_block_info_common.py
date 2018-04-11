#!/usr/bin/env python3
# coding=utf-8

import time
import random
from sawtooth_block_info.common import create_block_address

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 5
#########################################################################################

def test_create_block_address(benchmark):
    block_num = random.randint(50000, 5000000)
    benchmark.pedantic(create_block_address, kwargs = {'block_num':block_num}, \
    iterations=ITERATIONS, rounds=ROUNDS)