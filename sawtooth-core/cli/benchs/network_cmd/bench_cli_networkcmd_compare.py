#!/usr/bin/env python3
# coding=utf-8

import argparse
import random
import string

from sawtooth_cli.network_command.compare import get_tails
from sawtooth_cli.network_command.compare import build_fork_graph
from sawtooth_cli.network_command.compare import get_node_id_map
from sawtooth_cli.network_command.compare import print_table
from sawtooth_cli.network_command.compare import print_tree
from sawtooth_cli.network_command.compare import print_summary

from sawtooth_cli.network_command.fork_graph import SimpleBlock


#########################################################################################
VERBOSE_LEVEL = 1
LOOP = 100000
ITERATIONS = 1
ROUNDS = 10

CHAIN_INFO = [
        (15, ['z', '', '', '', '']),
        (14, ['y', '', '', '', '']),
        (13, ['w', '', 'x', '', '']),
        (12, ['t', '', 'u', '', 'v']),
        (11, ['g', 'h', 'l', 'm', 's']),
        (10, ['f', 'f', 'k', 'k', 'r']),
        (9, ['e', 'e', 'j', 'j', 'q']),
        (8, ['d', 'd', 'i', 'i', 'p']),
        (7, ['c', 'c', 'c', 'c', 'o']),
        (6, ['b', 'b', 'b', 'b', 'n']),
        (5, ['a', 'a', 'a', 'a', 'a']),
        (4, ['0', '0', '0', '0', '0']),
    ]
#########################################################################################


class NetworkCommandUtils():
    
    @staticmethod
    def make_chains(chains_info):

        def make_generator(collection):
            for item in collection:
                yield item

        chains = [[] for _ in chains_info[0][1]]
        for i, num_ids in enumerate(chains_info[:-1]):
            num, ids = num_ids
            for j, ident in enumerate(ids):
                if ident != '':
                    next_chain_info = chains_info[i + 1]
                    previous = next_chain_info[1][j]
                    block = SimpleBlock(num, ident, previous)
                    chains[j].append(block)
        chains = {
            i: make_generator(chain)
            for i, chain in enumerate(chains)
        }
        return chains


#########################################################################################
def test_compare_get_tails(benchmark):
    @benchmark
    def do_test_compare_get_tails():
        chains = NetworkCommandUtils.make_chains(CHAIN_INFO)
        try:
            get_tails(chains= chains)
        except Exception as e:
            print("type error: " + str(e))

#########################################################################################
def test_compare_build_fork_graph(benchmark):
    @benchmark
    def do_test_compare_build_fork_graph():
        good_chains_info = [
                (8, ['d', 'd', 'i', 'i', 'p']),
                (7, ['c', 'c', 'c', 'c', 'o']),
        ]

        bad_chains_info = [
            (6, ['b', 'b', '', 'b', 'n']),
            (5, ['a', 'a', '', 'a', '']),
            (4, ['0', '0', '', '0', '']),
        ]

        good_chains = NetworkCommandUtils.make_chains(good_chains_info)
        bad_chains =  NetworkCommandUtils.make_chains(bad_chains_info)
        tails, _ = get_tails(good_chains)
        try:
            build_fork_graph(chains = bad_chains, tails= tails)
        except Exception as e:
            print("type error: " + str(e))

#########################################################################################
def test_compare_get_node_id_map(benchmark):
    @benchmark
    def do_test_compare_get_node_id_map():
        good_chains_info = [
                (8, ['d', 'd', 'i', 'i', 'p']),
                (7, ['c', 'c', 'c', 'c', 'o']),
        ]
        good_chains = NetworkCommandUtils.make_chains(good_chains_info)
        get_node_id_map(unreporting=[], total = len(good_chains))

#########################################################################################
def test_compare_print_table(benchmark):
    @benchmark
    def do_test_compare_print_table():
        chains = NetworkCommandUtils.make_chains(CHAIN_INFO)
        tails, _ = get_tails(chains)
        graph, _ = build_fork_graph(chains, tails)
        node_id_map = get_node_id_map([], len(tails))
        tails = list(map(lambda item: item[1], sorted(tails.items())))
        print_table(graph = graph, tails= tails, node_id_map = node_id_map)

#########################################################################################
def test_compare_print_tree(benchmark):
    @benchmark
    def do_test_compare_print_tree():
        chains = NetworkCommandUtils.make_chains(CHAIN_INFO)
        tails, _ = get_tails(chains)
        graph, _ = build_fork_graph(chains, tails)
        node_id_map = get_node_id_map([], len(tails))
        tails = list(map(lambda item: item[1], sorted(tails.items())))
        print_tree(graph = graph, tails= tails, node_id_map = node_id_map)

#########################################################################################
def test_compare_print_summary(benchmark):
    @benchmark
    def do_test_compare_print_summary():
        chains = NetworkCommandUtils.make_chains(CHAIN_INFO)
        tails, _ = get_tails(chains)
        graph, _ = build_fork_graph(chains, tails)
        node_id_map = get_node_id_map([], len(tails))
        tails = list(map(lambda item: item[1], sorted(tails.items())))
        print_summary(graph = graph, tails = tails, node_id_map = node_id_map)