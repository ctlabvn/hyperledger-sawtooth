#!/usr/bin/env python3
# coding=utf-8


import os
import sys
from sawtooth_settings.processor.main import create_console_handler
from sawtooth_settings.processor.main import setup_loggers
from sawtooth_settings.processor.main import create_parser

from sawtooth_sdk.processor.core import TransactionProcessor

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 5
#########################################################################################

def test_create_console_handler(benchmark):
    benchmark.pedantic(create_console_handler, kwargs = {'verbose_level':VERBOSE_LEVEL}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_setup_loggers(benchmark):
    address = 'tcp://127.0.0.1:4004'
    transactionProcessor =  TransactionProcessor(address)
    benchmark.pedantic(setup_loggers, kwargs = {'verbose_level':VERBOSE_LEVEL, 'processor': transactionProcessor}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_create_parser(benchmark):
    prog_name=os.path.basename(sys.argv[0])
    benchmark.pedantic(create_parser, kwargs = {'prog_name':prog_name}, \
    iterations=ITERATIONS, rounds=ROUNDS)    