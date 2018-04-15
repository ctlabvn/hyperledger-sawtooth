#!/usr/bin/env python3
# coding=utf-8

import os
import sys
from sawtooth_identity.processor.handler import _setting_key_to_address
from sawtooth_identity.processor.handler import _get_role_address
from sawtooth_identity.processor.handler import _get_policy_address
from sawtooth_processor_test.mock_validator import MockValidator
from sawtooth_identity.processor.main import setup_loggers
from sawtooth_identity.processor.main import create_console_handler
from sawtooth_identity.processor.main import load_identity_config
from sawtooth_identity.processor.main import create_parser
from sawtooth_identity.processor.main import create_identity_config


from sawtooth_identity.processor.handler import IdentityTransactionHandler
from sawtooth_sdk.processor.core import TransactionProcessor

from sawtooth_identity.processor.config.identity import \
    load_default_identity_config
from sawtooth_sdk.processor.config import get_config_dir
from sawtooth_identity.processor.config.identity import \
    load_toml_identity_config

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10
DISTRIBUTION_NAME = 'sawadm'

TEST_KEY = "aaaaaa.bbbbbb.cccccccc"
POLICY_NAME = "deny_all_keys"

ALLOWED_SIGNER_ADDRESS = \
    "000000a87cb5eafdcca6a8689f6a627384c7dcf91e6901b1da081ee3b0c44298fc1c14"
#########################################################################################

def test_setting_key_to_address(benchmark):
    benchmark.pedantic(_setting_key_to_address, kwargs = {'key':TEST_KEY}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_handler_get_role_address(benchmark):
    benchmark.pedantic(_get_role_address, kwargs = {'role_name':TEST_KEY}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_create_console_handler(benchmark):
    benchmark.pedantic(create_console_handler, kwargs = {'verbose_level':VERBOSE_LEVEL}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_create_parser(benchmark):
    prog_name=os.path.basename(sys.argv[0])
    benchmark.pedantic(create_parser, kwargs = {'prog_name':prog_name}, \
    iterations=ITERATIONS, rounds=ROUNDS)    

# def test_setup_loggers(benchmark):
#     address = 'tcp://127.0.0.1:4004'
#     transactionProcessor =  TransactionProcessor(address)
#     benchmark.pedantic(setup_loggers, kwargs = {'verbose_level':VERBOSE_LEVEL, 'processor':transactionProcessor}, \
#     iterations=ITERATIONS, rounds=ROUNDS)