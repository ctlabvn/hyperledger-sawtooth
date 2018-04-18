#!/usr/bin/env python3
# coding=utf-8

import argparse
from sawtooth_cli.network_command.peers import add_peers_parser
from sawtooth_cli.network_command.peers import _add_list_parser

#########################################################################################
VERBOSE_LEVEL = 1
#########################################################################################

def test_add_peers_parser(benchmark):
    @benchmark
    def do_test_add_peers_parser():
        _parser = argparse.ArgumentParser(add_help=False)
        parent_parser = argparse.ArgumentParser(prog='test_keygen', add_help=False)
        subparsers = _parser.add_subparsers(title='subcommands', dest='command')
        add_peers_parser(subparsers = subparsers, parent_parser= parent_parser)

def test_add_list_parser(benchmark):
    @benchmark
    def do_test_add_list_parser():
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
        _add_list_parser(parser = peers_parsers, parent_parser = parent_parser)