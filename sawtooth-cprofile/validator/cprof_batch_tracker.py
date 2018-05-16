import cProfile

from unittest.mock import Mock

from sawtooth_validator.protobuf import batch_pb2
from sawtooth_validator.protobuf import transaction_pb2
from sawtooth_validator.state.batch_tracker import BatchTracker

def make_batch(batch_id, txn_id):
    transaction = transaction_pb2.Transaction(header_signature=txn_id)
    batch = batch_pb2.Batch(
        header_signature=batch_id, transactions=[transaction])

    return batch

def get_invalid_txn_infos():
    # create mock object
    block_store = Mock()
    batch_tracker = BatchTracker(block_store)

    batch_tracker.notify_batch_pending(
        make_batch("good_batch", "good_txn"))
    batch_tracker.notify_batch_pending(
        make_batch("bad_batch", "bad_txn"))

    batch_tracker.notify_txn_invalid("good_txn")
    batch_tracker.get_invalid_txn_info(batch_id= "bad_batch")

if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_batch_tracker.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    get_invalid_txn_infos()

    pr.disable()
    pr.print_stats(sort='time')