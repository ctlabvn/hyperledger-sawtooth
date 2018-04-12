#!/usr/bin/env python3
# coding=utf-8

import argparse

from sawtooth_cli.sawnet import create_parent_parser

from sawtooth_cli.network_command.list_blocks import add_list_blocks_parser

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10

PROGRAM_NAME = "Sawtooth_core_benchmark"
#########################################################################################

def test_add_list_blocks_parser(benchmark):
    parent_parser = create_parent_parser(PROGRAM_NAME)
    parser = argparse.ArgumentParser(
        description='Inspect status of a sawtooth network',
        parents=[parent_parser],)
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
    subparsers.required = True

    benchmark.pedantic(add_list_blocks_parser, kwargs = {'subparsers':subparsers, 'parent_parser': parent_parser}, \
    iterations=ITERATIONS, rounds=ROUNDS)