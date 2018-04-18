#!/usr/bin/env python3
# coding=utf-8

import os
import unittest
import tempfile
import argparse

from sawtooth_cli.protobuf.batch_pb2 import BatchHeader
from sawtooth_cli.protobuf.batch_pb2 import Batch
from sawtooth_cli.protobuf.batch_pb2 import BatchList
# from sawtooth_cli.protobuf.genesis_pb2 import GenesisData
from sawtooth_cli.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_cli.protobuf.transaction_pb2 import Transaction

from sawtooth_cli.admin_command import genesis
# from sawtooth_cli.exceptions import CliException

#########################################################################################

TEMP_DIR = tempfile.mkdtemp()
_parser = argparse.ArgumentParser(add_help=False)
TMP_DATA_DIR = tempfile.mkdtemp()
#########################################################################################

class TestBenchmarkCliGenesis():

    @staticmethod
    def make_batch(batch_sig, *txns):
        txn_ids = [txn.header_signature for txn in txns]
        batch_header = BatchHeader(signer_public_key='test_public_key',
                                   transaction_ids=txn_ids).SerializeToString()

        batch = Batch(
            header=batch_header,
            header_signature=batch_sig,
            transactions=txns
        )

        batch_list = BatchList(batches=[batch])
        target_path = os.path.join(TEMP_DIR, batch_sig + ".batch")
        with open(target_path, "wb") as f:
            filename = f.name
            f.write(batch_list.SerializeToString())

        return filename


    @staticmethod
    def transaction(txn_sig, dependencies):
        header = TransactionHeader(
            signer_public_key='test_public_key',
            family_name='test_family',
            family_version='1.0',
            inputs=[],
            outputs=[],
            dependencies=dependencies,
            payload_sha512='some_sha512',
            batcher_public_key='test_public_key'
        ).SerializeToString()

        return Transaction(
            header=header,
            header_signature=txn_sig,
            payload=b'')

    @staticmethod
    def parse_command(batch_filenames, with_default_output=False):
        cmd_args = ['genesis']

        if not with_default_output:
            cmd_args += ['-o', os.path.join(TEMP_DIR, 'genesis.batch')]
        
        cmd_args += batch_filenames
        return _parser.parse_args(cmd_args)

#########################################################################################
def test_add_genesis_parser(benchmark):
    @benchmark
    def do_test_add_genesis_parser():
        parent_parser = argparse.ArgumentParser(prog='test_genesis',add_help=False)
        subparsers = _parser.add_subparsers(title='subcommands', dest='command')
        genesis.add_genesis_parser(subparsers = subparsers, parent_parser = parent_parser)
#########################################################################################
def test_do_genesis(benchmark):
    @benchmark
    def do_test_do_genesis():
        batches = [TestBenchmarkCliGenesis.make_batch('batch1',
                                    TestBenchmarkCliGenesis.transaction('id1', []),
                                    TestBenchmarkCliGenesis.transaction('id2', []),
                                    TestBenchmarkCliGenesis.transaction('id3', [])),
                        TestBenchmarkCliGenesis.make_batch('batch2',
                                    TestBenchmarkCliGenesis.transaction('id4', ['id1', 'id2']))]
        
        args = TestBenchmarkCliGenesis.parse_command(batches)
        genesis.do_genesis(args=args, data_dir= TMP_DATA_DIR)
