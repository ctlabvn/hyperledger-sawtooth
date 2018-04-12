#!/usr/bin/env python3
# coding=utf-8


from sawtooth_cli.main import create_console_handler
from sawtooth_cli.main import create_parent_parser
from sawtooth_cli.main import create_parser
from sawtooth_cli.main import main_wrapper

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10

PROGRAM_NAME = "prog_name"
#########################################################################################

def test_create_console_handler(benchmark):
    benchmark.pedantic(create_console_handler, kwargs = {'verbose_level':VERBOSE_LEVEL}, \
    iterations=ITERATIONS, rounds=ROUNDS)
    
def test_create_parent_parser(benchmark):
    benchmark.pedantic(create_parent_parser, kwargs = {'prog_name':PROGRAM_NAME}, \
    iterations=ITERATIONS, rounds=ROUNDS)

# def test_main_wrapper(benchmark):
#     benchmark.pedantic(main_wrapper, iterations=ITERATIONS, rounds=ROUNDS)