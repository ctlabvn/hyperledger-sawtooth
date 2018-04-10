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

# pylint: disable=pointless-statement

import logging
import unittest

from sawtooth_validator.database.dict_database import DictDatabase
from sawtooth_validator.journal.block_store import BlockStore
from sawtooth_validator.journal.block_wrapper import NULL_BLOCK_IDENTIFIER
from sawtooth_validator.journal.block_wrapper import BlockWrapper

from sawtooth_validator.protobuf.block_pb2 import Block
from sawtooth_validator.protobuf.block_pb2 import BlockHeader

from test_journal.block_tree_manager import BlockTreeManager


LOGGER = logging.getLogger(__name__)



block_tree_manager = BlockTreeManager()

def do_chain_head():
    """ Test that the chain head can be retrieved from the
    BlockStore.
    """
    block = create_block()
    block_store = create_block_store(
        {
            block.header_signature: block
        })
    chain_head = block_store.chain_head

    return block, chain_head 

def test_chain_head(benchmark):
    block, chain_head = benchmark(do_chain_head)
    assert chain_head == block


def do_get_batch_by_transaction():
    """ Test BlockStore retrieval of a Batch that contains a specific
    transaction.
    """
    block = create_block()
    block_store = create_block_store()
    block_store.update_chain([block])

    batch = block.batches[0]
    txn_id = batch.transactions[0].header_signature
    stored = block_store.get_batch_by_transaction(txn_id)
    return stored, batch

def test_get_batch_by_transaction(benchmark):
    stored, batch = benchmark(do_get_batch_by_transaction)
    assert encode(stored) == encode(batch)    
   
    
def create_block_store(data=None):
    return BlockStore(DictDatabase(
        data, indexes=BlockStore.create_index_configuration()))

def create_block():
    return block_tree_manager.create_block()


def encode(obj):
    return obj.SerializeToString()






