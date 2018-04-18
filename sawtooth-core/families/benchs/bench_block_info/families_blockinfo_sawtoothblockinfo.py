#!/usr/bin/env python3
# coding=utf-8

import time
import random
from sawtooth_block_info.common import create_block_address

from sawtooth_block_info.injector import BlockInfoInjector
from sawtooth_validator.journal.batch_injector import \
    DefaultBatchInjectorFactory
from test_journal.block_tree_manager import BlockTreeManager
from test_journal.mock import MockStateViewFactory

from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfo


#########################################################################################
VERBOSE_LEVEL = 1
ITERATIONS = 1
ROUNDS = 10

BLOCKINFO_SIGNER_PUBLIC_KEY = "2" * 66
BLOCKINFO_HEADER_SIGNATURE = "1" * 128
BLOCKINFO_PREVIOUS_BLOCKID = "0" * 128
#########################################################################################

def test_common_create_block_address(benchmark):
    @benchmark
    def do_test_common_create_block_address():
        block_num = random.randint(50000, 5000000)
        create_block_address(block_num = block_num)

def test_injector_blockinfoinject_create_batch(benchmark):
    @benchmark
    def do_test_injector_blockinfoinject_create_batch():
        block_info = BlockInfo(
            block_num=100,
            signer_public_key=BLOCKINFO_SIGNER_PUBLIC_KEY,
            header_signature=BLOCKINFO_HEADER_SIGNATURE,
            timestamp=2364657,
            previous_block_id=BLOCKINFO_PREVIOUS_BLOCKID)

        btm = BlockTreeManager()
        batch_injector_factory=DefaultBatchInjectorFactory(\
                            block_store=btm.block_store,\
                            state_view_factory=MockStateViewFactory(btm.state_db),\
                            signer=btm.identity_signer)

        blockinjector = BlockInfoInjector(batch_injector_factory._block_store, \
        batch_injector_factory._state_view_factory, batch_injector_factory._signer)
        blockinjector.create_batch(block_info=block_info)
    