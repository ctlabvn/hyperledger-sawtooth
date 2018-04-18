#!/usr/bin/env python3
# coding=utf-8

import argparse
import random
import string
from sawtooth_cli.admin_command.keygen import add_keygen_parser
from sawtooth_cli.admin_command.keygen import do_keygen
from sawtooth_cli.admin_command import keygen

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10
#########################################################################################

def test_add_keygen_parser(benchmark):
    @benchmark
    def do_test_add_keygen_parser():
        _parser = argparse.ArgumentParser(add_help=False)
        parent_parser = argparse.ArgumentParser(prog='test_keygen', add_help=False)
        subparsers = _parser.add_subparsers(title='subcommands', dest='command')
        add_keygen_parser(subparsers=subparsers, parent_parser=parent_parser)


# def test_do_keygen(benchmark):
#     _parser = argparse.ArgumentParser(add_help=False)

#     def _parse_keygen_command(*args):
#         cmd_args = ['keygen']
#         cmd_args += args
#         return _parser.parse_args(cmd_args)

#     parent_parser = argparse.ArgumentParser(prog='test_keygen', add_help=False)
#     subparsers = _parser.add_subparsers(title='subcommands', dest='command')
#     keygen.add_keygen_parser(subparsers, parent_parser)
#     TEST_KEY = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
#     args = _parse_keygen_command(TEST_KEY)

#     benchmark.pedantic(keygen.do_keygen, kwargs = {'args':args}, \
#     iterations=ITERATIONS, rounds=ROUNDS)