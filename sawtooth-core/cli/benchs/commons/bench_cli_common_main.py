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
    @benchmark
    def do_test_create_console_handler():
        create_console_handler(verbose_level= VERBOSE_LEVEL)
    
def test_create_parent_parser(benchmark):
    @benchmark
    def do_test_create_parent_parser():
        create_parent_parser(prog_name= PROGRAM_NAME)

# def test_main_wrapper(benchmark):
#     benchmark.pedantic(main_wrapper, iterations=ITERATIONS, rounds=ROUNDS)