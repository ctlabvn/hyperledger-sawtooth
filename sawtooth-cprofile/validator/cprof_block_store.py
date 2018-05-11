import cProfile
import logging
import time

from test_journal.block_tree_manager import BlockTreeManager
from sawtooth_validator.database.dict_database import DictDatabase
from sawtooth_validator.journal.block_store import BlockStore

if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_block_store.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    block_tree_manager = BlockTreeManager()
    block = block_tree_manager.create_block()
    block_store = BlockStore(DictDatabase({
        block.header_signature: block,
    }, indexes=BlockStore.create_index_configuration()))
    block_store.update_chain([block])

    batch_id = block.batches[0].header_signature
    stored = block_store.get_block_by_batch_id(batch_id)

    batch = block.batches[0]
    txn_id = batch.transactions[0].header_signature
    stored = block_store.get_batch_by_transaction(txn_id)

    batch_id = batch.header_signature
    stored_batch = block_store.get_batch(batch_id)

    pr.disable()
    pr.print_stats(sort='time')
