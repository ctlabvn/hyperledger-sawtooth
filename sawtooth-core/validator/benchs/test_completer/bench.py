# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

# pylint: disable=protected-access

import unittest
import random
import hashlib

import cbor

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_validator.journal.completer import Completer
from sawtooth_validator.database.dict_database import DictDatabase
from sawtooth_validator.journal.block_store import BlockStore
from sawtooth_validator.journal.block_wrapper import NULL_BLOCK_IDENTIFIER
from sawtooth_validator.protobuf.transaction_pb2 import TransactionHeader, \
    Transaction
from sawtooth_validator.protobuf.batch_pb2 import BatchHeader, Batch
from sawtooth_validator.protobuf.block_pb2 import BlockHeader, Block
from test_completer.mock import MockGossip


class TestCompleter():
    def __init__(self):
        self.block_store = BlockStore(DictDatabase(
            indexes=BlockStore.create_index_configuration()))
        self.gossip = MockGossip()
        self.completer = Completer(self.block_store, self.gossip)
        self.completer._on_block_received = self._on_block_received
        self.completer._on_batch_received = self._on_batch_received
        self.completer._has_block = self._has_block
        self._has_block_value = True

        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        crypto_factory = CryptoFactory(context)
        self.signer = crypto_factory.new_signer(private_key)

        self.blocks = []
        self.batches = []

    def _on_block_received(self, block):
        return self.blocks.append(block.header_signature)

    def _on_batch_received(self, batch):
        return self.batches.append(batch.header_signature)

    def _has_block(self, batch):
        return self._has_block_value

    def _create_transactions(self, count, missing_dep=False):
        txn_list = []

        for _ in range(count):
            payload = {
                'Verb': 'set',
                'Name': 'name' + str(random.randint(0, 100)),
                'Value': random.randint(0, 100)
            }
            intkey_prefix = \
                hashlib.sha512('intkey'.encode('utf-8')).hexdigest()[0:6]

            addr = intkey_prefix + \
                hashlib.sha512(payload["Name"].encode('utf-8')).hexdigest()

            payload_encode = hashlib.sha512(cbor.dumps(payload)).hexdigest()

            header = TransactionHeader(
                signer_public_key=self.signer.get_public_key().as_hex(),
                family_name='intkey',
                family_version='1.0',
                inputs=[addr],
                outputs=[addr],
                dependencies=[],
                batcher_public_key=self.signer.get_public_key().as_hex(),
                payload_sha512=payload_encode)

            if missing_dep:
                header.dependencies.extend(["Missing"])

            header_bytes = header.SerializeToString()

            signature = self.signer.sign(header_bytes)

            transaction = Transaction(
                header=header_bytes,
                payload=cbor.dumps(payload),
                header_signature=signature)

            txn_list.append(transaction)

        return txn_list

    def _create_batches(self, batch_count, txn_count,
                        missing_dep=False):

        batch_list = []

        for _ in range(batch_count):
            txn_list = self._create_transactions(txn_count,
                                                 missing_dep=missing_dep)
            txn_sig_list = [txn.header_signature for txn in txn_list]

            batch_header = BatchHeader(
                signer_public_key=self.signer.get_public_key().as_hex())
            batch_header.transaction_ids.extend(txn_sig_list)

            header_bytes = batch_header.SerializeToString()

            signature = self.signer.sign(header_bytes)

            batch = Batch(
                header=header_bytes,
                transactions=txn_list,
                header_signature=signature)

            batch_list.append(batch)

        return batch_list

    def _create_blocks(self,
                       block_count,
                       batch_count,
                       missing_predecessor=False,
                       missing_batch=False,
                       find_batch=True):
        block_list = []

        for i in range(0, block_count):
            batch_list = self._create_batches(batch_count, 2)
            batch_ids = [batch.header_signature for batch in batch_list]

            if missing_predecessor:
                predecessor = "Missing"
            else:
                predecessor = (block_list[i - 1].header_signature if i > 0 else
                               NULL_BLOCK_IDENTIFIER)

            block_header = BlockHeader(
                signer_public_key=self.signer.get_public_key().as_hex(),
                batch_ids=batch_ids,
                block_num=i,
                previous_block_id=predecessor)

            header_bytes = block_header.SerializeToString()

            signature = self.signer.sign(header_bytes)

            if missing_batch:
                if find_batch:
                    self.completer.add_batch(batch_list[-1])
                batch_list = batch_list[:-1]

            block = Block(
                header=header_bytes,
                batches=batch_list,
                header_signature=signature)

            block_list.append(block)

        return block_list




def test_good_block(benchmark):
    """
    Add completed block to completer. Block should be passed to
    on_block_recieved.
    """

    def do_good_block():
        testCompleter = TestCompleter()
        block = testCompleter._create_blocks(1, 1)[0]
        testCompleter.completer.add_block(block)
        return block, testCompleter

    block, testCompleter = benchmark(do_good_block)
    assert block.header_signature in testCompleter.blocks

def test_duplicate_block(benchmark):
    """
    Submit same block twice.
    """
    def do_duplicate_block():
        testCompleter = TestCompleter()
        block = testCompleter._create_blocks(1, 1)[0]
        testCompleter.completer.add_block(block)
        testCompleter.completer.add_block(block)
        return block, testCompleter

    block, testCompleter = benchmark(do_duplicate_block)
    assert block.header_signature in testCompleter.blocks
    assert len(testCompleter.blocks) == 1


def test_block_with_extra_batch(benchmark):
    """
    The block has a batch that is not in the batch_id list.
    """
    def do_block_with_extra_batch():
        testCompleter = TestCompleter()
        block = testCompleter._create_blocks(1, 1)[0]
        batches = testCompleter._create_batches(1, 1, True)
        block.batches.extend(batches)
        testCompleter.completer.add_block(block)
        return testCompleter

    testCompleter = benchmark(do_block_with_extra_batch)
    assert len(testCompleter.blocks) == 0


def test_good_batch(benchmark):
    """
    Add complete batch to completer. The batch should be passed to
    on_batch_received.
    """
    def do_good_batch():
        testCompleter = TestCompleter()
        batch = testCompleter._create_batches(1, 1)[0]
        testCompleter.completer.add_batch(batch)
        return batch, testCompleter

    batch, testCompleter = benchmark(do_good_batch)
    assert batch.header_signature in testCompleter.batches
    assert batch == testCompleter.completer.get_batch(batch.header_signature)

