import cProfile
import logging
import time

from test_client_request_handlers.mocks import MockBlockStore
from sawtooth_validator.protobuf.block_pb2 import BlockHeader
from sawtooth_validator.protobuf.batch_pb2 import Batch
from sawtooth_validator.protobuf.batch_pb2 import BatchHeader
from sawtooth_validator.protobuf.transaction_pb2 import Transaction
from sawtooth_validator.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_validator.database.dict_database import DictDatabase
from sawtooth_validator.state.merkle import MerkleDatabase
from sawtooth_validator.state.batch_tracker import BatchTracker



def make_db_and_store(size=3):
    database = DictDatabase()
    store = MockBlockStore(size=0)
    roots = []

    merkle = MerkleDatabase(database)
    data = {}

    # Create all the keys that will be used. Keys are zero-padded hex strings
    # starting with '1'.
    keys = [format(i, 'x').zfill(70) for i in range(1, size + 1)]

    for i in range(1, size + 1):
        # Construct the state for this root
        data = {}
        for key_idx in range(i):
            key = keys[key_idx]
            # Calculate unique values based on the key and root
            val = i + (2 * key_idx)
            data[key] = str(val).encode()

        root = merkle.update(data, virtual=False)
        roots.append(root)
        store.add_block(str(i), root)

    return database, store, roots


def _make_mock_transaction(base_id='id', payload='payload'):
    txn_id = 'c' * (128 - len(base_id)) + base_id
    header = TransactionHeader(
        batcher_public_key='public_key-' + base_id,
        family_name='family',
        family_version='0.0',
        nonce=txn_id,
        signer_public_key='public_key-' + base_id)
    return Transaction(
        header=header.SerializeToString(),
        header_signature=txn_id,
        payload=payload.encode())


def make_mock_batch(base_id='id'):
    batch_id = 'a' * (128 - len(base_id)) + base_id
    txn = _make_mock_transaction(base_id)

    header = BatchHeader(
        signer_public_key='public_key-' + base_id,
        transaction_ids=[txn.header_signature])

    return Batch(
        header=header.SerializeToString(),
        header_signature=batch_id,
        transactions=[txn])


def make_store_and_tracker(size=3):
    store = MockBlockStore(size=size)
    tracker = BatchTracker(store)
    tracker.notify_batch_pending(make_mock_batch('d'))
    tracker.notify_batch_pending(make_mock_batch('f'))
    tracker.notify_txn_invalid('c' * 127 + 'f', 'error message', b'error data')

    return store, tracker


if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_client_request_handlers.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    make_db_and_store(3)
    make_store_and_tracker(3)

    pr.disable()
    pr.print_stats(sort='time')
