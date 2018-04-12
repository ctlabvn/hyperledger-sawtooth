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


class TestBlockValidator():
    def __init__(self):
        self.state_view_factory = MockStateViewFactory()

        self.block_tree_manager = BlockTreeManager()
        self.root = self.block_tree_manager.chain_head

        self.block_validation_handler = self.BlockValidationHandler()
        self.permission_verifier = MockPermissionVerifier()


    # assertions

    def assert_valid_block(self, block):
        assert block.status == BlockStatus.Valid            

    def assert_invalid_block(self, block):
        assert block.status == BlockStatus.Invalid            

    def assert_unknown_block(self, block):
        assert block.status == BlockStatus.Unknown

    def assert_new_block_committed(self):
        self.assert_handler_has_result()
        assert self.block_validation_handler.commit_new_block == True           

    def assert_new_block_not_committed(self):
        self.assert_handler_has_result()
        assert self.block_validation_handler.commit_new_block == False

    def assert_handler_has_result(self):
        msg = "Validation handler doesn't have result"
        assert self.block_validation_handler.has_result() == True

    # block validation

    def validate_block(self, block):
        validator = self.create_block_validator()
        validator._load_consensus = lambda block: mock_consensus
        validator.process_block_verification(
            block,
            self.block_validation_handler.on_block_validated)

    def create_block_validator(self):
        return BlockValidator(
            state_view_factory=self.state_view_factory,
            block_cache=self.block_tree_manager.block_cache,
            transaction_executor=MockTransactionExecutor(
                batch_execution_result=None),
            squash_handler=None,
            identity_signer=self.block_tree_manager.identity_signer,
            data_dir=None,
            config_dir=None,
            permission_verifier=self.permission_verifier)

    class BlockValidationHandler(object):
        def __init__(self):
            self.commit_new_block = None
            self.result = None

        def on_block_validated(self, commit_new_block, result):
            self.commit_new_block = commit_new_block
            self.result = result

        def has_result(self):
            return not (self.result is None or self.commit_new_block is None)




    # block tree manager interface

    def generate_chain_with_head(self, root_block, num_blocks, params=None,
                                 exclude_head=True):
        chain = self.block_tree_manager.generate_chain(
            root_block, num_blocks, params, exclude_head)

        head = chain[-1]

        return chain, head

# fork based tests
def test_fork_simple(benchmark):
    """
    Test a simple case of a new block extending the current root.
    """

    testBlockValidator = TestBlockValidator()

    @benchmark
    def do_fork_simple():
        new_block = testBlockValidator.block_tree_manager.generate_block(
            previous_block=testBlockValidator.root,
            add_to_cache=True)

        testBlockValidator.validate_block(new_block)

        testBlockValidator.assert_valid_block(new_block)
        testBlockValidator.assert_new_block_committed()

def test_good_fork_lower(benchmark):
    """
    Test case of a new block extending on a valid chain but not as long
    as the current chain.
    """
    # create a new valid chain 5 long from the current root
    testBlockValidator = TestBlockValidator()

    @benchmark
    def do_good_fork_lower():
        _, head = testBlockValidator.generate_chain_with_head(
            testBlockValidator.root, 5, {'add_to_store': True})

        testBlockValidator.block_tree_manager.set_chain_head(head)

        # generate candidate chain 3 long from the same root
        _, new_head = testBlockValidator.generate_chain_with_head(
            testBlockValidator.root, 3, {'add_to_cache': True})

        testBlockValidator.validate_block(new_head)

        testBlockValidator.assert_valid_block(new_head)
        testBlockValidator.assert_new_block_not_committed()

def test_good_fork_higher(benchmark):
    """
    Test case of a new block extending on a valid chain but longer
    than the current chain. ( similar to test_good_fork_lower but uses
    a different code path when finding the common root )
    """

    testBlockValidator = TestBlockValidator()

    @benchmark
    def do_good_fork_higher():
        # create a new valid chain 5 long from the current root
        _, head = testBlockValidator.generate_chain_with_head(
            testBlockValidator.root, 5, {'add_to_store': True})

        testBlockValidator.block_tree_manager.set_chain_head(head)

        # generate candidate chain 8 long from the same root
        _, new_head = testBlockValidator.generate_chain_with_head(
            head, 8, {'add_to_cache': True})

        testBlockValidator.validate_block(new_head)

        testBlockValidator.assert_valid_block(new_head)
        testBlockValidator.assert_new_block_committed()

def test_fork_different_genesis(benchmark):
    """"
    Test the case where new block is from a different genesis
    """
    # create a new valid chain 5 long from the current root
    testBlockValidator = TestBlockValidator()

    @benchmark
    def do_fork_different_genesis():

        _, head = testBlockValidator.generate_chain_with_head(
            testBlockValidator.root, 5, {'add_to_store': True})

        testBlockValidator.block_tree_manager.set_chain_head(head)

        # generate candidate chain 5 long from its own genesis
        _, new_head = testBlockValidator.generate_chain_with_head(
            None, 5, {'add_to_cache': True})

        testBlockValidator.validate_block(new_head)

        testBlockValidator.assert_invalid_block(new_head)
        testBlockValidator.assert_new_block_not_committed()

def test_fork_missing_predecessor(benchmark):
    """"
    Test the case where new block is missing the a predecessor
    """
    # generate candidate chain 5 long off the current head.
    testBlockValidator = TestBlockValidator()

    @benchmark
    def do_fork_missing_predecessor():
        chain, head = testBlockValidator.generate_chain_with_head(
            testBlockValidator.root, 5, {'add_to_cache': True})

        # remove one of the new blocks
        del testBlockValidator.block_tree_manager.block_cache[chain[1].identifier]

        testBlockValidator.validate_block(head)

        testBlockValidator.assert_unknown_block(head)
        testBlockValidator.assert_new_block_not_committed()



class TestChainController():
    def __init__(self):
        self.block_tree_manager = BlockTreeManager()
        self.gossip = MockNetwork()
        self.txn_executor = MockTransactionExecutor()
        self.block_sender = MockBlockSender()
        self.chain_id_manager = MockChainIdManager()
        self._chain_head_lock = RLock()
        self.permission_verifier = MockPermissionVerifier()
        self.state_view_factory = MockStateViewFactory(
            self.block_tree_manager.state_db)
        self.transaction_executor = MockTransactionExecutor(
            batch_execution_result=None)
        self.executor = SynchronousExecutor()

        self.block_validator = BlockValidator(
            state_view_factory=self.state_view_factory,
            block_cache=self.block_tree_manager.block_cache,
            transaction_executor=self.transaction_executor,
            squash_handler=None,
            identity_signer=self.block_tree_manager.identity_signer,
            data_dir=None,
            config_dir=None,
            permission_verifier=self.permission_verifier,
            thread_pool=self.executor)

        def chain_updated(head, committed_batches=None,
                          uncommitted_batches=None):
            pass

        self.chain_ctrl = ChainController(
            block_cache=self.block_tree_manager.block_cache,
            block_validator=self.block_validator,
            state_view_factory=self.state_view_factory,
            chain_head_lock=self._chain_head_lock,
            on_chain_updated=chain_updated,
            chain_id_manager=self.chain_id_manager,
            data_dir=None,
            config_dir=None,
            chain_observers=[])

        init_root = self.chain_ctrl.chain_head
        self.assert_is_chain_head(init_root)

        # create a chain of length 5 extending the root
        _, head = self.generate_chain(init_root, 5)
        self.receive_and_process_blocks(head)
        self.assert_is_chain_head(head)

        self.init_head = head

    

    # next multi threaded
    # next add block publisher
    # next batch lists
    # integrate with LMDB
    # early vs late binding ( class member of consensus BlockPublisher)

    # helpers

    def assert_is_chain_head(self, block):
        chain_head_sig = self.chain_ctrl.chain_head.header_signature
        block_sig = block.header_signature

        # assert chain_head_sig[:8] == block_sig[:8]
            

    def generate_chain(self, root_block, num_blocks, params=None):
        '''Returns (chain, chain_head).
        Usually only the head is needed,
        but occasionally the chain itself is used.
        '''
        if params is None:
            params = {'add_to_cache': True}

        chain = self.block_tree_manager.generate_chain(
            root_block, num_blocks, params)

        head = chain[-1]

        return chain, head

    def generate_block(self, *args, **kwargs):
        return self.block_tree_manager.generate_block(
            *args, **kwargs)

    def receive_and_process_blocks(self, *blocks):
        for block in blocks:
            self.chain_ctrl.on_block_received(block)
        self.executor.process_all()


def test_simple_case(benchmark):
    testChainController = TestChainController()
    @benchmark
    def do_simple_case():
        new_block = testChainController.generate_block(testChainController.init_head)
        testChainController.receive_and_process_blocks(new_block)
        testChainController.assert_is_chain_head(new_block)

def test_alternate_genesis(benchmark):
    '''Tests a fork extending an alternate genesis block
    '''
    testChainController = TestChainController()
    @benchmark
    def do_alternate_genesis():
        chain, _ = testChainController.generate_chain(None, 5)

        for block in chain:
            testChainController.receive_and_process_blocks(block)

        # make sure initial head is still chain head
        testChainController.assert_is_chain_head(testChainController.init_head)


def test_bad_blocks(benchmark):
    '''Tests bad blocks extending current chain
    '''
    # Bad due to consensus
    testChainController = TestChainController()
    @benchmark
    def do_bad_blocks():
        bad_consen = testChainController.generate_block(
            previous_block=testChainController.init_head,
            invalid_consensus=True)

        # chain head should be the same
        testChainController.receive_and_process_blocks(bad_consen)
        testChainController.assert_is_chain_head(testChainController.init_head)

        # Bad due to transaction
        bad_batch = testChainController.generate_block(
            previous_block=testChainController.init_head,
            invalid_batch=True)

        # chain head should be the same
        testChainController.receive_and_process_blocks(bad_batch)
        testChainController.assert_is_chain_head(testChainController.init_head)

        # # Ensure good block works
        good_block = testChainController.generate_block(
            previous_block=testChainController.init_head)

        # chain head should be good_block
        testChainController.receive_and_process_blocks(good_block)
        testChainController.assert_is_chain_head(good_block)


def test_fork_weights(benchmark):
    '''Tests extending blocks of different weights
    '''
    testChainController = TestChainController()
    @benchmark
    def do_fork_weights():
        weight_4 = testChainController.generate_block(
            previous_block=testChainController.init_head,
            weight=4)

        weight_7 = testChainController.generate_block(
            previous_block=testChainController.init_head,
            weight=7)

        weight_8 = testChainController.generate_block(
            previous_block=testChainController.init_head,
            weight=8)

        testChainController.receive_and_process_blocks(
            weight_7,
            weight_4,
            weight_8)

        testChainController.assert_is_chain_head(weight_8)


def test_fork_lengths(benchmark):
    '''Tests competing forks of different lengths
    '''

    testChainController = TestChainController()
    @benchmark
    def do_fork_lengths():
        _, head_2 = testChainController.generate_chain(testChainController.init_head, 2)
        _, head_7 = testChainController.generate_chain(testChainController.init_head, 7)
        _, head_5 = testChainController.generate_chain(testChainController.init_head, 5)

        testChainController.receive_and_process_blocks(
            head_2,
            head_7,
            head_5)

        testChainController.assert_is_chain_head(head_7)


def test_advancing_chain(benchmark):
    '''Tests the chain being advanced between a fork's
    creation and validation
    '''
    testChainController = TestChainController()
    @benchmark
    def do_advancing_chain():
        _, fork_5 = testChainController.generate_chain(testChainController.init_head, 5)
        _, fork_3 = testChainController.generate_chain(testChainController.init_head, 3)

        testChainController.receive_and_process_blocks(fork_3)
        testChainController.assert_is_chain_head(fork_3)

        # fork_5 is longer than fork_3, so it should be accepted
        testChainController.receive_and_process_blocks(fork_5)
        testChainController.assert_is_chain_head(fork_5)



def test_advancing_fork(benchmark):
    '''Tests a fork advancing before getting validated
    '''

    testChainController = TestChainController()
    @benchmark
    def do_advancing_fork():
        _, fork_head = testChainController.generate_chain(testChainController.init_head, 5)

        testChainController.chain_ctrl.on_block_received(fork_head)

        # advance fork before it gets accepted
        _, ext_head = testChainController.generate_chain(fork_head, 3)

        testChainController.executor.process_all()

        testChainController.assert_is_chain_head(fork_head)

        testChainController.receive_and_process_blocks(ext_head)

        testChainController.assert_is_chain_head(ext_head)


def test_multiple_extended_forks(benchmark):
    '''A more involved example of competing forks

    Three forks of varying lengths a_0, b_0, and c_0
    are created extending the existing chain, with c_0
    being the longest initially. The chains are extended
    in the following sequence:

    1. Extend all forks by 2. The c fork should remain the head.
    2. Extend forks by lenths such that the b fork is the
       longest. It should be the new head.
    3. Extend all forks by 8. The b fork should remain the head.
    4. Create a new fork of the initial chain longer than
       any of the other forks. It should be the new head.
    '''

    testChainController = TestChainController()
    @benchmark
    def do_multiple_extended_forks():
        # create forks of various lengths
        _, a_0 = testChainController.generate_chain(testChainController.init_head, 3)
        _, b_0 = testChainController.generate_chain(testChainController.init_head, 5)
        _, c_0 = testChainController.generate_chain(testChainController.init_head, 7)

        testChainController.receive_and_process_blocks(a_0, b_0, c_0)
        testChainController.assert_is_chain_head(c_0)

        # extend every fork by 2
        _, a_1 = testChainController.generate_chain(a_0, 2)
        _, b_1 = testChainController.generate_chain(b_0, 2)
        _, c_1 = testChainController.generate_chain(c_0, 2)

        testChainController.receive_and_process_blocks(a_1, b_1, c_1)
        testChainController.assert_is_chain_head(c_1)

        # extend the forks by different lengths
        _, a_2 = testChainController.generate_chain(a_1, 1)
        _, b_2 = testChainController.generate_chain(b_1, 6)
        _, c_2 = testChainController.generate_chain(c_1, 3)

        testChainController.receive_and_process_blocks(a_2, b_2, c_2)
        testChainController.assert_is_chain_head(b_2)

        # extend every fork by 2
        _, a_3 = testChainController.generate_chain(a_2, 8)
        _, b_3 = testChainController.generate_chain(b_2, 8)
        _, c_3 = testChainController.generate_chain(c_2, 8)

        testChainController.receive_and_process_blocks(a_3, b_3, c_3)
        testChainController.assert_is_chain_head(b_3)

        # create a new longest chain
        _, wow = testChainController.generate_chain(testChainController.init_head, 30)
        testChainController.receive_and_process_blocks(wow)
        testChainController.assert_is_chain_head(wow)


class TestChainControllerGenesisPeer():
    def __init__(self):
        self.block_tree_manager = BlockTreeManager(with_genesis=False)
        self.gossip = MockNetwork()
        self.txn_executor = MockTransactionExecutor()
        self.block_sender = MockBlockSender()
        self.chain_id_manager = MockChainIdManager()
        self.chain_head_lock = RLock()
        self.permission_verifier = MockPermissionVerifier()
        self.state_view_factory = MockStateViewFactory(
            self.block_tree_manager.state_db)
        self.transaction_executor = MockTransactionExecutor(
            batch_execution_result=None)
        self.executor = SynchronousExecutor()

        self.block_validator = BlockValidator(
            state_view_factory=self.state_view_factory,
            block_cache=self.block_tree_manager.block_cache,
            transaction_executor=self.transaction_executor,
            squash_handler=None,
            identity_signer=self.block_tree_manager.identity_signer,
            data_dir=None,
            config_dir=None,
            permission_verifier=self.permission_verifier,
            thread_pool=self.executor)

        def chain_updated(head, committed_batches=None,
                          uncommitted_batches=None):
            pass

        self.chain_ctrl = ChainController(
            block_cache=self.block_tree_manager.block_cache,
            block_validator=self.block_validator,
            state_view_factory=self.state_view_factory,
            chain_head_lock=self.chain_head_lock,
            on_chain_updated=chain_updated,
            chain_id_manager=self.chain_id_manager,
            data_dir=None,
            config_dir=None,
            chain_observers=[])

        self.assertIsNone(self.chain_ctrl.chain_head)

    def assertIsNone(self, value):
        assert value == None


def test_genesis_block_mismatch(benchmark):
    '''Test mismatch block chain id will drop genesis block.
    Given a ChainController with an empty chain
    mismatches the block-chain-id stored on disk.
    '''

    testChainControllerGenesisPeer = TestChainControllerGenesisPeer()
    @benchmark
    def do_genesis_block_mismatch():
        testChainControllerGenesisPeer.chain_id_manager.save_block_chain_id('my_chain_id')
        some_other_genesis_block = \
            testChainControllerGenesisPeer.block_tree_manager.generate_genesis_block()
        testChainControllerGenesisPeer.chain_ctrl.on_block_received(some_other_genesis_block)

        testChainControllerGenesisPeer.assertIsNone(testChainControllerGenesisPeer.chain_ctrl.chain_head)

def test_genesis_block_matches_block_chain_id(benchmark):
    '''Test that a validator with no chain will accept a valid genesis
    block that matches the block-chain-id stored on disk.
    '''

    testChainControllerGenesisPeer = TestChainControllerGenesisPeer()
    @benchmark
    def do_genesis_block_matches_block_chain_id():
        my_genesis_block = testChainControllerGenesisPeer.block_tree_manager.generate_genesis_block()
        chain_id = my_genesis_block.header_signature
        testChainControllerGenesisPeer.chain_id_manager.save_block_chain_id(chain_id)

        with patch.object(BlockValidator,
                          'validate_block',
                          return_value=True):
            testChainControllerGenesisPeer.chain_ctrl.on_block_received(my_genesis_block)

        assert testChainControllerGenesisPeer.chain_ctrl.chain_head != None
        chain_head_sig = testChainControllerGenesisPeer.chain_ctrl.chain_head.header_signature

        # assert chain_head_sig[:8] == chain_id[:8]
        assert chain_id == testChainControllerGenesisPeer.chain_id_manager.get_block_chain_id()



class TestJournal():
    def __init__(self):
        self.gossip = MockNetwork()
        self.txn_executor = MockTransactionExecutor()
        self.block_sender = MockBlockSender()
        self.batch_sender = MockBatchSender()
        self.permission_verifier = MockPermissionVerifier()


def test_publish_block(benchmark):
    """
    Test that the Journal will produce blocks and consume those blocks
    to extend the chain.
    :return:
    """
    # construction and wire the journal to the
    # gossip layer.

    testJournal = TestJournal()
    @benchmark
    def do_publish_block():
        btm = BlockTreeManager()
        block_publisher = None
        chain_controller = None
        try:
            block_publisher = BlockPublisher(
                transaction_executor=testJournal.txn_executor,
                block_cache=btm.block_cache,
                state_view_factory=MockStateViewFactory(btm.state_db),
                settings_cache=SettingsCache(
                    SettingsViewFactory(
                        btm.state_view_factory),
                ),
                block_sender=testJournal.block_sender,
                batch_sender=testJournal.batch_sender,
                squash_handler=None,
                chain_head=btm.block_store.chain_head,
                identity_signer=btm.identity_signer,
                data_dir=None,
                config_dir=None,
                permission_verifier=testJournal.permission_verifier,
                check_publish_block_frequency=0.1,
                batch_observers=[],
                batch_injector_factory=DefaultBatchInjectorFactory(
                    block_store=btm.block_store,
                    state_view_factory=MockStateViewFactory(btm.state_db),
                    signer=btm.identity_signer))

            block_validator = BlockValidator(
                state_view_factory=MockStateViewFactory(btm.state_db),
                block_cache=btm.block_cache,
                transaction_executor=testJournal.txn_executor,
                squash_handler=None,
                identity_signer=btm.identity_signer,
                data_dir=None,
                config_dir=None,
                permission_verifier=testJournal.permission_verifier)

            chain_controller = ChainController(
                block_cache=btm.block_cache,
                block_validator=block_validator,
                state_view_factory=MockStateViewFactory(btm.state_db),
                chain_head_lock=block_publisher.chain_head_lock,
                on_chain_updated=block_publisher.on_chain_updated,
                chain_id_manager=None,
                data_dir=None,
                config_dir=None,
                chain_observers=[])

            testJournal.gossip.on_batch_received = block_publisher.queue_batch
            testJournal.gossip.on_block_received = chain_controller.queue_block

            block_publisher.start()
            chain_controller.start()

            # feed it a batch
            batch = Batch()
            block_publisher.queue_batch(batch)

            wait_until(lambda: testJournal.block_sender.new_block is not None, 2)
            assert testJournal.block_sender.new_block != None

            block = BlockWrapper(testJournal.block_sender.new_block)
            chain_controller.queue_block(block)

            # wait for the chain_head to be updated.
            wait_until(lambda: btm.chain_head.identifier ==
                       block.identifier, 2)
            # assert btm.chain_head.identifier == block.identifier
        finally:
            if block_publisher is not None:
                block_publisher.stop()
            if chain_controller is not None:
                chain_controller.stop()
            if block_validator is not None:
                block_validator.stop()


class TestChainCommitState():
    """Test for:
    - No duplicates found for batches
    - No duplicates found for transactions
    - Duplicate batch found in current chain
    - Duplicate batch found in fork
    - Duplicate transaction found in current chain
    - Duplicate transaction found in fork
    - Missing dependencies caught
    - Dependencies found for transactions in current chain
    - Dependencies found for transactions in fork
    """

    def gen_block(self, block_id, prev_id, num, batches):
        return BlockWrapper(
            Block(
                header_signature=block_id,
                batches=batches,
                header=BlockHeader(
                    block_num=num,
                    previous_block_id=prev_id).SerializeToString()))

    def gen_batch(self, batch_id, transactions):
        return Batch(header_signature=batch_id, transactions=transactions)

    def gen_txn(self, txn_id, deps=None):
        return Transaction(
            header_signature=txn_id,
            header=TransactionHeader(dependencies=deps).SerializeToString())
    

    def create_new_chain(self):
        """
        NUM     0  1  2  3  4  5  6
        CURRENT B0-B1-B2-B3-B4-B5-B6
                         |
        FORK             +--B7-B8-B9
        """
        txns = [
            self.gen_txn('t' + format(i, 'x'))
            for i in range(10)
        ]
        batches = [
            self.gen_batch('b' + format(i, 'x'), [txns[i]])
            for i in range(10)
        ]
        committed_blocks = [
            self.gen_block(
                block_id='B0',
                prev_id=NULL_BLOCK_IDENTIFIER,
                num=0,
                batches=[batches[0]])
        ]
        committed_blocks.extend([
            self.gen_block(
                block_id='B' + format(i, 'x'),
                prev_id='B' + format(i - 1, 'x'),
                num=i,
                batches=[batches[i]])
            for i in range(1, 7)
        ])
        uncommitted_blocks = [
            self.gen_block(
                block_id='B7',
                prev_id='B3',
                num=4,
                batches=[batches[0]])
        ]
        uncommitted_blocks.extend([
            self.gen_block(
                block_id='B' + format(i, 'x'),
                prev_id='B' + format(i - 1, 'x'),
                num=5 + (i - 8),
                batches=[batches[i]])
            for i in range(8, 10)
        ])

        return txns, batches, committed_blocks, uncommitted_blocks

    def create_chain_commit_state(
        self,
        committed_blocks,
        uncommitted_blocks,
        head_id,
    ):
        block_store = BlockStore(DictDatabase(
            indexes=BlockStore.create_index_configuration()))
        block_store.update_chain(committed_blocks)

        block_cache = BlockCache(
            block_store=block_store)

        for block in uncommitted_blocks:
            block_cache[block.header_signature] = block

        return ChainCommitState(head_id, block_cache, block_store)


# Batches
def test_no_duplicate_batch_found(benchmark):
    """Verify that DuplicateBatch is not raised for a completely new
    batch.
    """
    testChainCommitState = TestChainCommitState()
    @benchmark
    def do_no_duplicate_batch_found():
        _, _, committed_blocks, uncommitted_blocks =\
            testChainCommitState.create_new_chain()

        commit_state = testChainCommitState.create_chain_commit_state(
            committed_blocks, uncommitted_blocks, 'B6')

        commit_state.check_for_duplicate_batches([testChainCommitState.gen_batch('b10', [])])



# Dependencies
def test_present_dependency(benchmark):
    """Verify that a present dependency is found."""
    testChainCommitState = TestChainCommitState()
    @benchmark
    def do_present_dependency():
        transactions, _, committed_blocks, uncommitted_blocks =\
            testChainCommitState.create_new_chain()

        commit_state = testChainCommitState.create_chain_commit_state(
            committed_blocks, uncommitted_blocks, 'B6')

        commit_state.check_for_transaction_dependencies([
            testChainCommitState.gen_txn('t10', deps=[transactions[2].header_signature])
        ])



def test_present_dependency_in_fork(benchmark):
    """Verify that a dependency present in the fork is found.
    """
    testChainCommitState = TestChainCommitState()
    @benchmark
    def do_present_dependency_in_fork():
        transactions, _, committed_blocks, uncommitted_blocks =\
            testChainCommitState.create_new_chain()

        commit_state = testChainCommitState.create_chain_commit_state(
            committed_blocks, uncommitted_blocks, 'B9')

        commit_state.check_for_transaction_dependencies([
            testChainCommitState.gen_txn('t10', deps=[transactions[8].header_signature])
        ])



def test_block_event_extractor(benchmark):
    """Test that a sawtooth/block-commit event is generated correctly."""
    testChainCommitState = TestChainCommitState()
    @benchmark
    def do_block_event_extractor():
        block_header = BlockHeader(
            block_num=85,
            state_root_hash="0987654321fedcba",
            previous_block_id="0000000000000000")
        block = BlockWrapper(Block(
            header_signature="abcdef1234567890",
            header=block_header.SerializeToString()))
        extractor = BlockEventExtractor(block)
        events = extractor.extract([EventSubscription(
            event_type="sawtooth/block-commit")])
        assert events == [
            Event(
                event_type="sawtooth/block-commit",
                attributes=[
                    Event.Attribute(key="block_id", value="abcdef1234567890"),
                    Event.Attribute(key="block_num", value="85"),
                    Event.Attribute(
                        key="state_root_hash", value="0987654321fedcba"),
                    Event.Attribute(
                        key="previous_block_id",
                        value="0000000000000000")])]



def test_tf_events(benchmark):
    """Test that tf events are generated correctly."""
    testChainCommitState = TestChainCommitState()
    @benchmark
    def do_tf_events():
        gen_data = [
            ["test1", "test2"],
            ["test3"],
            ["test4", "test5", "test6"],
        ]
        event_sets = [
            [
                Event(event_type=event_type)
                for event_type in events
            ] for events in gen_data
        ]
        receipts = [
            TransactionReceipt(events=events)
            for events in event_sets
        ]
        extractor = ReceiptEventExtractor(receipts)

        events = extractor.extract([])
        assert [] == events

        events = extractor.extract([
            EventSubscription(event_type="test1"),
            EventSubscription(event_type="test5"),
        ])
        assert events == [event_sets[0][0], event_sets[2][1]]

def test_state_delta_events(benchmark):
    """Test that sawtooth/state-delta events are generated correctly."""
    testChainCommitState = TestChainCommitState()
    @benchmark
    def do_state_delta_events():
        gen_data = [
            [("a", b"a", StateChange.SET), ("b", b"b", StateChange.DELETE)],
            [("a", b"a", StateChange.DELETE), ("d", b"d", StateChange.SET)],
            [("e", b"e", StateChange.SET)],
        ]
        change_sets = [
            [
                StateChange(address=address, value=value, type=change_type)
                for address, value, change_type in state_changes
            ] for state_changes in gen_data
        ]
        receipts = [
            TransactionReceipt(state_changes=state_changes)
            for state_changes in change_sets
        ]
        extractor = ReceiptEventExtractor(receipts)

        factory = EventFilterFactory()
        events = extractor.extract([
            EventSubscription(
                event_type="sawtooth/state-delta",
                filters=[factory.create("address", "a")]),
            EventSubscription(
                event_type="sawtooth/state-delta",
                filters=[factory.create(
                    "address", "[ce]", EventFilter.REGEX_ANY)],
            )
        ])
        assert events == [Event(
            event_type="sawtooth/state-delta",
            attributes=[
                Event.Attribute(key="address", value=address)
                for address in ["e", "d", "a", "b"]
            ],
            data=StateChangeList(state_changes=[
                change_sets[2][0], change_sets[1][1],
                change_sets[1][0], change_sets[0][1],
            ]).SerializeToString(),
        )]
