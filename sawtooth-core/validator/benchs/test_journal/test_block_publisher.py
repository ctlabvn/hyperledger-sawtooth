# Copyright 2016 Intel Corporation
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

# pylint: disable=too-many-lines
# pylint: disable=pointless-statement
# pylint: disable=protected-access
# pylint: disable=unbalanced-tuple-unpacking

import logging
from threading import RLock
import unittest
from unittest.mock import patch

from sawtooth_validator.database.dict_database import DictDatabase

from sawtooth_validator.journal.block_cache import BlockCache
from sawtooth_validator.journal.block_wrapper import BlockStatus
from sawtooth_validator.journal.block_wrapper import BlockWrapper
from sawtooth_validator.journal.block_wrapper import NULL_BLOCK_IDENTIFIER

from sawtooth_validator.journal.block_store import BlockStore
from sawtooth_validator.journal.block_validator import BlockValidator
from sawtooth_validator.journal.block_validator import BlockValidationFailure
from sawtooth_validator.journal.chain import ChainController
from sawtooth_validator.journal.chain_commit_state import ChainCommitState
from sawtooth_validator.journal.chain_commit_state import DuplicateTransaction
from sawtooth_validator.journal.chain_commit_state import DuplicateBatch
from sawtooth_validator.journal.chain_commit_state import MissingDependency
from sawtooth_validator.journal.publisher import BlockPublisher
from sawtooth_validator.journal.timed_cache import TimedCache
from sawtooth_validator.journal.event_extractors \
    import BlockEventExtractor
from sawtooth_validator.journal.event_extractors \
    import ReceiptEventExtractor
from sawtooth_validator.journal.batch_injector import \
    DefaultBatchInjectorFactory

from sawtooth_validator.server.events.subscription import EventSubscription
from sawtooth_validator.server.events.subscription import EventFilterFactory

from sawtooth_validator.protobuf.transaction_pb2 import Transaction
from sawtooth_validator.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_validator.protobuf.batch_pb2 import Batch
from sawtooth_validator.protobuf.block_pb2 import Block
from sawtooth_validator.protobuf.block_pb2 import BlockHeader
from sawtooth_validator.protobuf.transaction_receipt_pb2 import \
    TransactionReceipt
from sawtooth_validator.protobuf.transaction_receipt_pb2 import StateChange
from sawtooth_validator.protobuf.transaction_receipt_pb2 import StateChangeList
from sawtooth_validator.protobuf.events_pb2 import Event
from sawtooth_validator.protobuf.events_pb2 import EventFilter

from sawtooth_validator.state.settings_view import SettingsViewFactory
from sawtooth_validator.state.settings_cache import SettingsCache

from test_journal.block_tree_manager import BlockTreeManager

from test_journal.mock import MockChainIdManager
from test_journal.mock import MockBlockSender
from test_journal.mock import MockBatchSender
from test_journal.mock import MockNetwork
from test_journal.mock import MockStateViewFactory, CreateSetting
from test_journal.mock import MockTransactionExecutor
from test_journal.mock import MockPermissionVerifier
from test_journal.mock import SynchronousExecutor
from test_journal.mock import MockBatchInjectorFactory
from test_journal.utils import wait_until

from test_journal import mock_consensus


LOGGER = logging.getLogger(__name__)


def test_load_from_block_store(benchmark):
    """ Test that misses will load from the block store.
    """
    def do_load_from_block_store():
        bs = {}
        block1 = Block(
            header=BlockHeader(previous_block_id="000").SerializeToString(),
            header_signature="test")
        bs["test"] = BlockWrapper(block1)
        block2 = Block(
            header=BlockHeader(previous_block_id="000").SerializeToString(),
            header_signature="test2")
        blkw2 = BlockWrapper(block2)
        bs["test2"] = blkw2
        bc = BlockCache(bs)
        return bc, blkw2

    bc, blkw2 = benchmark(do_load_from_block_store)    
    assert "test" in bc
    assert bc["test2"] == blkw2


class TestBlockPublisher():
    '''
    The block publisher has three main functions, and in these tests
    those functions are given the following wrappers for convenience:
        * on_batch_received -> receive_batches
        * on_chain_updated -> update_chain_head
        * on_check_publish_block -> publish_block

    After publishing a block, publish_block sends its block to the
    mock block sender, and that block is named result_block. This block
    is what is checked by the test assertions.

    The basic pattern for the publisher tests (with variations) is:
        0) make a list of batches (usually in setUp);
        1) receive the batches;
        2) publish a block;
        3) verify the block (checking that it contains the correct batches,
           or checking that it doesn't exist, or whatever).

    The publisher chain head might be updated several times in a test.
    '''

    def __init__(self):

        self.block_tree_manager = BlockTreeManager()
        self.block_sender = MockBlockSender()
        self.batch_sender = MockBatchSender()
        self.state_view_factory = MockStateViewFactory({})
        self.permission_verifier = MockPermissionVerifier()

        self.publisher = BlockPublisher(
            transaction_executor=MockTransactionExecutor(),
            block_cache=self.block_tree_manager.block_cache,
            state_view_factory=self.state_view_factory,
            settings_cache=SettingsCache(
                SettingsViewFactory(
                    self.block_tree_manager.state_view_factory),
            ),
            block_sender=self.block_sender,
            batch_sender=self.batch_sender,
            squash_handler=None,
            chain_head=self.block_tree_manager.chain_head,
            identity_signer=self.block_tree_manager.identity_signer,
            data_dir=None,
            config_dir=None,
            check_publish_block_frequency=0.1,
            batch_observers=[],
            permission_verifier=self.permission_verifier)

        self.init_chain_head = self.block_tree_manager.chain_head

        self.result_block = None

        # A list of batches is created at the beginning of each test.
        # The test assertions and the publisher function wrappers
        # take these batches as a default argument.
        self.batch_count = 8
        self.batches = self.make_batches()              

    def verify_block(self, batches=None):
        if batches is None:
            batches = self.batches

        batch_count = None if batches is None else len(batches)        

    # publisher functions

    def receive_batch(self, batch):
        self.publisher.on_batch_received(batch)

    def receive_batches(self, batches=None):
        if batches is None:
            batches = self.batches

        for batch in batches:
            self.receive_batch(batch)

    def publish_block(self):
        self.publisher.on_check_publish_block()
        self.result_block = self.block_sender.new_block
        self.block_sender.new_block = None

    def update_chain_head(self, head, committed=None, uncommitted=None):
        if head:
            self.block_tree_manager.block_store.update_chain([head])
        self.publisher.on_chain_updated(
            chain_head=head,
            committed_batches=committed,
            uncommitted_batches=uncommitted)

    # batches
    def make_batch(self, missing_deps=False, txn_count=2):
        return self.block_tree_manager.generate_batch(
            txn_count=txn_count,
            missing_deps=missing_deps)

    def make_batches(self, batch_count=None, missing_deps=False):
        if batch_count is None:
            batch_count = self.batch_count

        return [self.make_batch(missing_deps=missing_deps)
                for _ in range(batch_count)]

    def make_batches_with_duplicate_txn(self):
        txns = [self.batches[0].transactions[0],
                self.block_tree_manager.generate_transaction("nonce")]
        return [self.block_tree_manager.generate_batch(txns=txns)]


def test_publish(benchmark):
    # Publish a block with several batches
    
    testBlockPublisher = TestBlockPublisher()

    @benchmark
    def do_publish():
        testBlockPublisher.receive_batches()
        testBlockPublisher.publish_block()
        testBlockPublisher.verify_block()


def test_reject_duplicate_batches_from_receive(benchmark):    
    # Test that duplicate batches from on_batch_received are rejected
    
    testBlockPublisher = TestBlockPublisher()

    @benchmark
    def do_reject_duplicate_batches_from_receive():
        for _ in range(5):
            testBlockPublisher.receive_batches()
        testBlockPublisher.publish_block()
        testBlockPublisher.verify_block()            

def test_reject_duplicate_batches_from_store(benchmark):
    '''
    Test that duplicate batches from block store are rejected
    '''
    testBlockPublisher = TestBlockPublisher()
    @benchmark
    def do_reject_duplicate_batches_from_store():
        testBlockPublisher.update_chain_head(None)

        testBlockPublisher.update_chain_head(
            head=testBlockPublisher.init_chain_head,
            uncommitted=testBlockPublisher.batches)

        testBlockPublisher.receive_batches()

        testBlockPublisher.publish_block()

        testBlockPublisher.verify_block()


def test_committed_batches(benchmark):
    '''
    Test that batches committed upon updating the chain head
    are not included in the next block.
    '''

    testBlockPublisher = TestBlockPublisher()

    @benchmark
    def do_committed_batches():
        testBlockPublisher.update_chain_head(None)

        testBlockPublisher.update_chain_head(
            head=testBlockPublisher.init_chain_head,
            committed=testBlockPublisher.batches)

        new_batches = testBlockPublisher.make_batches(batch_count=12)

        testBlockPublisher.receive_batches(new_batches)

        testBlockPublisher.publish_block()

        testBlockPublisher.verify_block(new_batches)



def test_batch_injection_start_block(benchmark):
    '''
    Test that the batch is injected at the beginning of the block.
    '''
    testBlockPublisher = TestBlockPublisher()

    @benchmark
    def do_batch_injection_start_block():
        injected_batch = testBlockPublisher.make_batch()

        testBlockPublisher.publisher = BlockPublisher(
            transaction_executor=MockTransactionExecutor(),
            block_cache=testBlockPublisher.block_tree_manager.block_cache,
            state_view_factory=testBlockPublisher.state_view_factory,
            settings_cache=SettingsCache(
                SettingsViewFactory(
                    testBlockPublisher.block_tree_manager.state_view_factory),
            ),
            block_sender=testBlockPublisher.block_sender,
            batch_sender=testBlockPublisher.batch_sender,
            squash_handler=None,
            chain_head=testBlockPublisher.block_tree_manager.chain_head,
            identity_signer=testBlockPublisher.block_tree_manager.identity_signer,
            data_dir=None,
            config_dir=None,
            permission_verifier=testBlockPublisher.permission_verifier,
            check_publish_block_frequency=0.1,
            batch_observers=[],
            batch_injector_factory=MockBatchInjectorFactory(injected_batch))

        testBlockPublisher.receive_batches()

        testBlockPublisher.publish_block()


