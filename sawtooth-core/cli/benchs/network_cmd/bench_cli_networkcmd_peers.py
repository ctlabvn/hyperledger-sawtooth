#!/usr/bin/env python3
# coding=utf-8

import argparse
from sawtooth_cli.network_command.peers import add_peers_parser
from sawtooth_cli.network_command.peers import _add_list_parser

#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10
#########################################################################################

def test_add_peers_parser(benchmark):
    _parser = argparse.ArgumentParser(add_help=False)
    parent_parser = argparse.ArgumentParser(prog='test_keygen', add_help=False)
    subparsers = _parser.add_subparsers(title='subcommands', dest='command')
    benchmark.pedantic(add_peers_parser, kwargs = {'subparsers':subparsers, 'parent_parser': parent_parser}, \
    iterations=ITERATIONS, rounds=ROUNDS)

def test_add_list_parser(benchmark):
    _parser = argparse.ArgumentParser(add_help=False)
    parent_parser = argparse.ArgumentParser(prog='test_keygen', add_help=False)
    subparsers = _parser.add_subparsers(title='subcommands', dest='command')

    help_text = 'Shows the peering arrangment of a network'
    parser = subparsers.add_parser(
        'peers',
        help=help_text,
        description='{}.'.format(help_text))

    peers_parsers = parser.add_subparsers(
        title='subcommands',
        dest='peers_command')
    peers_parsers.required = True

    benchmark.pedantic(_add_list_parser, kwargs = {'parser':peers_parsers, 'parent_parser': parent_parser}, \
    iterations=ITERATIONS, rounds=ROUNDS) 