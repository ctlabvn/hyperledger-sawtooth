# Copyright 2018 Intel Corporation
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
from unittest.mock import Mock

from sawtooth_validator.protobuf import batch_pb2
from sawtooth_validator.protobuf import transaction_pb2
from sawtooth_validator.state.batch_tracker import BatchTracker


def make_batch(batch_id, txn_id):
    transaction = transaction_pb2.Transaction(header_signature=txn_id)
    batch = batch_pb2.Batch(
        header_signature=batch_id, transactions=[transaction])

    return batch 

def test_invalid_txn_infos(benchmark):
        """Test that the invalid batch information is return correctly.

        - Add valid batch info
        - Add invalid batch info
        - Ensure that the invalid batch info is returned
        - Ensure that modifying the returned info does not affect future calls
        """
        # create mock object
        block_store = Mock()
        batch_tracker = BatchTracker(block_store)

        batch_tracker.notify_batch_pending(
            make_batch("good_batch", "good_txn"))
        batch_tracker.notify_batch_pending(
            make_batch("bad_batch", "bad_txn"))

        batch_tracker.notify_txn_invalid("good_txn")

        invalid_info = benchmark(batch_tracker.get_invalid_txn_info, "bad_batch")
        assert 0 == len(invalid_info)



