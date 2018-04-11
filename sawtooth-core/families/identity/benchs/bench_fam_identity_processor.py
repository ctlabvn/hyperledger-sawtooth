#!/usr/bin/env python3
# coding=utf-8

import os
import sys
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_processor_test.mock_validator import MockValidator
from sawtooth_identity.processor.main import setup_loggers
from sawtooth_identity.processor.main import create_console_handler
from sawtooth_identity.processor.main import load_identity_config
from sawtooth_identity.processor.main import create_parser
from sawtooth_identity.processor.main import create_identity_config

from sawtooth_identity.processor.config.identity import \
    load_default_identity_config
from sawtooth_sdk.processor.config import get_config_dir
from sawtooth_identity.processor.config.identity import \
    load_toml_identity_config

    

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 5

ALLOWED_SIGNER_ADDRESS = \
    "000000a87cb5eafdcca6a8689f6a627384c7dcf91e6901b1da081ee3b0c44298fc1c14"
#########################################################################################

# def test_load_identity_config(benchmark):
#     args = ['/project/families/identity/benchs/bench_fam_identity_processor.py']
    
#     prog_name=os.path.basename(sys.argv[0])
#     parser = create_parser(prog_name)
#     args = parser.parse_args(args)
#     arg_config = create_identity_config(args)

#     benchmark(load_identity_config, kwargs = {'first_config':arg_config})

def test_create_console_handler(benchmark):
    benchmark.pedantic(create_console_handler, kwargs = {'verbose_level':VERBOSE_LEVEL}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_create_parser(benchmark):
    prog_name=os.path.basename(sys.argv[0])
    benchmark.pedantic(create_parser, kwargs = {'prog_name':prog_name}, \
    iterations=ITERATIONS, rounds=ROUNDS)    

def test_setup_loggers(benchmark):
    address = 'tcp://127.0.0.1:4004'
    transactionProcessor =  TransactionProcessor(address)
    benchmark.pedantic(setup_loggers, kwargs = {'verbose_level':VERBOSE_LEVEL, 'processor':transactionProcessor}, \
    iterations=ITERATIONS, rounds=ROUNDS)