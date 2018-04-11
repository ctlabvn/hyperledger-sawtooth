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

import sawtooth_validator.state.client_handlers as handlers
from sawtooth_validator.protobuf import client_transaction_pb2
from sawtooth_validator.protobuf.transaction_pb2 import Transaction
from test_client_request_handlers.base_case import ClientHandlerTestCase
from test_client_request_handlers.mocks import MockBlockStore


B_0 = 'b' * 127 + '0'
B_1 = 'b' * 127 + '1'
B_2 = 'b' * 127 + '2'
C_0 = 'c' * 127 + '0'
C_1 = 'c' * 127 + '1'
C_2 = 'c' * 127 + '2'

clientHanlerTestCase = ClientHandlerTestCase()


def setUp():
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.TransactionListRequest(store),
        client_transaction_pb2.ClientTransactionListRequest,
        client_transaction_pb2.ClientTransactionListResponse,
        store=store)

def test_txn_list_request(benchmark):
    """Verifies requests for txn lists without parameters work properly.

    Queries the default mock block store with three blocks:
        {
            header_signature: 'bbb...2',
            batches: [{
                header_signature: 'aaa...2',
                transactions: [{
                    header_signature: 'ccc...2',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with start of C_2 and limit 100
        - a list of transactions with 3 items
        - those items are instances of Transaction
        - the first item has a header_signature of 'ccc...2'
    """
    # response = clientHanlerTestCase.make_request()
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id    
    assert 3 == len(response.transactions)    
    assert C_2 == response.transactions[0].header_signature


def test_txn_list_with_head(benchmark):
    """Verifies requests for txn lists work properly with a head id.

    Queries the default mock block store with 'bbb...1' as the head:
        {
            header_signature: 'bbb...1',
            batches: [{
                header_signature: 'aaa...1',
                transactions: [{
                    header_signature: 'ccc...1',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...1'
        - a paging response with start of C_1 and limit 100
        - a list of transactions with 2 items
        - those items are instances of Transaction
        - the first item has a header_signature of 'ccc...1'
    """
    # response = clientHanlerTestCase.make_request(head_id=B_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'head_id': B_1})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.head_id
    assert 2 == len(response.transactions)
    assert C_1 == response.transactions[0].header_signature


def test_txn_list_filtered_by_ids(benchmark):
    """Verifies requests for txn lists work filtered by txn ids.

    Queries the default mock block store with three blocks:
        {
            header_signature: 'bbb...2',
            batches: [{
                header_signature: 'aaa...2',
                transactions: [{
                    header_signature: 'ccc...2',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with start of C_0 and limit 100
        - a list of transactions with 2 items
        - the items are instances of Transaction
        - the first item has a header_signature of 'ccc...0'
        - the second item has a header_signature of 'ccc...2'
    """
    # response = clientHanlerTestCase.make_request(transaction_ids=[C_0, C_2])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'transaction_ids': [C_0, C_2]})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 2 == len(response.transactions)
    assert C_0 == response.transactions[0].header_signature
    assert C_2 == response.transactions[1].header_signature


def test_txn_list_by_head_and_ids(benchmark):
    """Verifies txn list requests work with both head and txn ids.

    Queries the default mock block store with 'bbb...1' as the head:
        {
            header_signature: 'bbb...1',
            batches: [{
                header_signature: 'aaa...1',
                transactions: [{
                    header_signature: 'ccc...1',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...1'
        - a paging response with a start of C_0 and limit 100
        - a list of transactions with 1 item
        - that item is an instance of Transaction
        - that item has a header_signature of 'ccc...0'
    """
    # response = clientHanlerTestCase.make_request(head_id=B_1, transaction_ids=[C_0])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'transaction_ids': [C_0], 'head_id': B_1})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.head_id
    assert 1 == len(response.transactions)
    assert C_0 == response.transactions[0].header_signature


def test_txn_list_paginated(benchmark):
    """Verifies requests for txn lists work when paginated just by limit.

    Queries the default mock block store:
        {
            header_signature: 'bbb...2',
            batches: [{
                header_signature: 'aaa...2',
                transactions: [{
                    header_signature: 'ccc...2',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with:
            * a next_id of C_0
            * the default start of C_2
            * limit of 2
        - a list of transactions with 2 items
        - those items are instances of Transaction
        - the first item has a header_signature of 'ccc...2'
    """
    # response = clientHanlerTestCase.make_paged_request(limit=2)
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 2})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 2 == len(response.transactions)
    assert C_2 == response.transactions[0].header_signature

def test_txn_list_paginated_by_start_id(benchmark):
    """Verifies txn list requests work paginated by limit and start_id.

    Queries the default mock block store:
        {
            header_signature: 'bbb...2',
            batches: [{
                header_signature: 'aaa...2',
                transactions: [{
                    header_signature: 'ccc...2',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with:
            * a next_id of C_0
            * a start of C_1
            * limit of 1
        - a list of transactions with 1 item
        - that item is an instance of Transaction
        - that item has a header_signature of 'ccc...1'
    """
    # response = clientHanlerTestCase.make_paged_request(limit=1, start=C_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 1, 'start': C_1})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 1 == len(response.transactions)
    assert C_1 == response.transactions[0].header_signature

def test_txn_list_paginated_by_index(benchmark):
    """Verifies txn list requests work paginated by limit and min_index.

    Queries the default mock block store:
        {
            header_signature: 'bbb...2',
            batches: [{
                header_signature: 'aaa...2',
                transactions: [{
                    header_signature: 'ccc...2',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with a next of C_1, start of C_2 and limit of 1
        - a list of transactions with 1 item
        - that item is an instance of Transaction
        - that item has a header_signature of 'ccc...2'
    """
    # response = clientHanlerTestCase.make_paged_request(limit=1, start=C_2)
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 1, 'start': C_2})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 1 == len(response.transactions)
    assert C_2 == response.transactions[0].header_signature



def test_txn_list_paginated_with_head(benchmark):
    """Verifies txn list requests work with both paging and a head id.

    Queries the default mock block store with 'bbb...1' as the head:
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...1'
        - a paging response with:
            * a start of C_0
            * limit of 1
        - a list of transactions with 1 item
        - that item is an instance of Transaction
        - that has a header_signature of 'ccc...0'
    """
    # response = clientHanlerTestCase.make_paged_request(limit=1, start=C_0, head_id=B_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 1, 'start': C_0, 'head_id': B_1})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.head_id
    assert 1 == len(response.transactions)
    assert C_0 == response.transactions[0].header_signature

def test_txn_list_sorted_in_reverse(benchmark):
    """Verifies txn list requests work sorted by a key in reverse.

    Queries the default mock block store:
        {
            header_signature: 'bbb...2',
            batches: [{
                header_signature: 'aaa...2',
                transactions: [{
                    header_signature: 'ccc...2',
                    ...
                }],
                ...
            }],
            ...
        },
        {header_signature: 'bbb...1', ...},
        {header_signature: 'bbb...0', ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response start of C_0 and limit of 100
        - a list of transactions with 3 items
        - the items are instances of Transaction
        - the first item has a header_signature of 'ccc...0'
        - the last item has a header_signature of 'ccc...2'
    """
    controls = clientHanlerTestCase.make_sort_controls('default', reverse=True)
    # response = clientHanlerTestCase.make_request(sorting=controls)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'sorting': controls})

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 3 == len(response.transactions)
    assert C_0 == response.transactions[0].header_signature
    assert C_2 == response.transactions[2].header_signature



def setUp2():
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.TransactionGetRequest(store),
        client_transaction_pb2.ClientTransactionGetRequest,
        client_transaction_pb2.ClientTransactionGetResponse)

def test_txn_get_request(benchmark):
    """Verifies requests for a specific txn by id work properly.

    Queries the default three block mock store for a txn id of 'ccc...1'

    Expects to find:
        - a status of OK
        - a transaction property which is an instances of Transaction
        - the transaction has a header_signature of 'ccc...1'
    """
    # response = clientHanlerTestCase.make_request(transaction_id=C_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'transaction_id': C_1})

    assert clientHanlerTestCase.status.OK == response.status
    assert C_1 == response.transaction.header_signature


def test_txn_get_with_block_id(benchmark):
    """Verifies requests for a specific txn break properly with a block id.

    Expects to find:
        - a status of NO_RESOURCE
        - that the Transaction returned, when serialized, is actually empty
    """
    # response = clientHanlerTestCase.make_request(transaction_id=B_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'transaction_id': B_1})

    assert clientHanlerTestCase.status.NO_RESOURCE == response.status
