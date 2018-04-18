#!/usr/bin/env python3
# coding=utf-8

import argparse

from sawtooth_cli.sawnet import create_parent_parser

from sawtooth_cli.network_command.list_blocks import add_list_blocks_parser

#########################################################################################
VERBOSE_LEVEL = 1
PROGRAM_NAME = "Sawtooth_core_benchmark"
#########################################################################################

def test_add_list_blocks_parser(benchmark):
    @benchmark
    def do_test_add_list_blocks_parser():
        parent_parser = create_parent_parser(PROGRAM_NAME)
        parser = argparse.ArgumentParser(
            description='Inspect status of a sawtooth network',
            parents=[parent_parser],)
        subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
        subparsers.required = True
        add_list_blocks_parser(subparsers = subparsers, parent_parser = parent_parser)