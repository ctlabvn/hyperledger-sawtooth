#!/usr/bin/env python3
# coding=utf-8
from sawtooth_block_info.processor.main import create_parser
from sawtooth_block_info.processor.main import create_console_handler
from sawtooth_block_info.processor.main import load_block_info_config
from sawtooth_block_info.processor.main import setup_loggers
from sawtooth_block_info.processor.config.block_info import BlockInfoConfig
from sawtooth_sdk.processor.core import TransactionProcessor


#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10
DISTRIBUTION_NAME = 'sawadm'
#########################################################################################

def test_create_console_handler(benchmark):
    benchmark.pedantic(create_console_handler, kwargs = {'verbose_level':VERBOSE_LEVEL}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_processor_create_parser(benchmark):
    benchmark.pedantic(create_parser, kwargs = {'prog_name':DISTRIBUTION_NAME}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_create_block_info_config(benchmark):
    blockInfoConfig = BlockInfoConfig()
    benchmark.pedantic(load_block_info_config, kwargs = {'first_config':blockInfoConfig}, \
    iterations=ITERATIONS, rounds=ROUNDS)

# def test_setup_loggers(benchmark):
#     address = 'tcp://127.0.0.1:4004'
#     transactionProcessor =  TransactionProcessor(address)
#     benchmark.pedantic(setup_loggers, kwargs = {'verbose_level':VERBOSE_LEVEL, 'processor':transactionProcessor}, \
#     iterations=ITERATIONS, rounds=ROUNDS)
#     return