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
from sawtooth_validator.journal.block_store import BlockStore
from sawtooth_validator.protobuf import client_block_pb2
from sawtooth_validator.protobuf.block_pb2 import Block
from test_client_request_handlers.base_case import ClientHandlerTestCase
from test_client_request_handlers.mocks import MockBlockStore


B_0 = 'b' * 127 + '0'
B_1 = 'b' * 127 + '1'
B_2 = 'b' * 127 + '2'
A_1 = 'a' * 127 + '1'
C_1 = 'c' * 127 + '1'

# can not use more iterations with setup params, so increase rounds instead
clientHanlerTestCase = ClientHandlerTestCase()

def setUp():        
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.BlockListRequest(store),
        client_block_pb2.ClientBlockListRequest,
        client_block_pb2.ClientBlockListResponse,
        store=store)

def test_block_list_request(benchmark):
    """Verifies requests for block lists without parameters work properly.

    Queries the default mock block store with three blocks:
        {header: {block_num: 2 ...}, header_signature: 'bbb...2' ...},
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2' (the latest)
        - a paging response with start of 'b' * 127 + '2' and limit 100
        - a list of blocks with 3 items
        - the items are instances of Block
        - The first item has a header_signature of 'bbb...2'
    """
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 3 == len(response.blocks)
    assert B_2 == response.blocks[0].header_signature


def test_block_list_with_head(benchmark):
    """Verifies requests for lists of blocks work properly with a head id.

    Queries the default mock block store with '1' as the head:
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...}

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...1'
        - a paging response with start of B_2 and limit 100
        - a list of blocks with 2 items
        - the items are instances of Block
        - The first item has a header_signature of 'bbb...1'
    """
    # response = self.make_request(head_id=B_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, 
        kwargs={'head_id': B_1}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.head_id
    assert 2 == len(response.blocks)
    assert B_1 == response.blocks[0].header_signature


def test_block_list_filtered_by_ids(benchmark):
    """Verifies requests for lists of blocks work filtered by block ids.

    Queries the default mock block store with three blocks:
        {header: {block_num: 2 ...}, header_signature: 'bbb...2' ...},
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...},

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - an empty paging response
        - a list of blocks with 2 items
        - the items are instances of Block
        - the first item has a header_signature of 'bbb...0'
        - the second item has a header_signature of 'bbb...2'
    """
    # response = self.make_request(block_ids=[B_0, B_2])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, 
        kwargs={'block_ids': [B_0, B_2]}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 2 == len(response.blocks)
    assert B_0 == response.blocks[0].header_signature
    assert B_2 == response.blocks[1].header_signature


def test_block_list_by_head_and_ids(benchmark):
    """Verifies block list requests work with both head and block ids.

    Queries the default mock block store with '1' as the head:
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...},

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...1'
            - an empty paging response
        - a list of blocks with 1 item
        - that item is an instance of Block
        - that item has a header_signature of 'bbb...0'
    """
    # response = self.make_request(head_id=B_1, block_ids=[B_0])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, 
        kwargs={'head_id':B_1, 'block_ids': [B_0]}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.head_id
    assert 1 == len(response.blocks)
    assert B_0 == response.blocks[0].header_signature


def test_block_list_paginated(benchmark):
    """Verifies requests for block lists work when paginated just by limit.

    Queries the default mock block store with three blocks:
        {header: {block_num: 2 ...}, header_signature: B_2 ...},
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...},

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
         a paging response with start of B_@, limit 100 and
            next of B_0
        - a list of blocks with 2 items
        - those items are instances of Block
        - the first item has a header_signature of 'bbb...2'
    """
    # response = self.make_paged_request(limit=2)

    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, 
        kwargs={'limit':2}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 2 == len(response.blocks)
    assert B_2 == response.blocks[0].header_signature


def test_block_list_paginated_by_start(benchmark):
    """Verifies block list requests work paginated by limit and start.

    Queries the default mock block store with three blocks:
        {header: {block_num: 2 ...}, header_signature: 'bbb...2' ...},
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...},

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with:
            * a next_id of '0x0000000000000000
            * a limit of 100
            * start of '0x0000000000000001'
        - a list of blocks with 1 item
        - that item is an instance of Block
        - that item has a header_signature of 'bbb...1'
    """
    # response = self.make_paged_request(limit=1, start=BlockStore.block_num_to_hex(1))

    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, 
            kwargs={'limit':1, 'start':BlockStore.block_num_to_hex(1)}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id    
    assert 1 == len(response.blocks)
    assert B_1 == response.blocks[0].header_signature


def test_block_list_sorted_in_reverse(benchmark):
    """Verifies block list requests work sorted in reverse.

    Queries the default mock block store with three blocks:
        {header: {block_num: 2 ...}, header_signature: 'bbb...2' ...},
        {header: {block_num: 1 ...}, header_signature: 'bbb...1' ...},
        {header: {block_num: 0 ...}, header_signature: 'bbb...0' ...},

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2', the latest
        - a paging response with start of B_) and limit 100
        - a list of blocks with 3 items
        - the items are instances of Block
        - the first item has a header_signature of 'bbb...2'
        - the last item has a header_signature of 'bbb...0'
    """
    controls = clientHanlerTestCase.make_sort_controls('block_num', reverse=True)
    # response = self.make_request(sorting=controls)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, 
            kwargs={'sorting': controls}, rounds=10)
    

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 3 == len(response.blocks)
    assert B_0 == response.blocks[0].header_signature
    assert B_2 == response.blocks[2].header_signature



def setUp2():    
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.BlockGetByIdRequest(store),
        client_block_pb2.ClientBlockGetByIdRequest,
        client_block_pb2.ClientBlockGetResponse)


def test_block_get_request(benchmark):
    """Verifies requests for a specific block by id work properly.

    Queries the default three block mock store for an id of 'bbb...1'.
    Expects to find:
        - a status of OK
        - the block property which is an instances of Block
        - The block has a header_signature of 'bbb...1'
    """
    # response = self.make_request(block_id=B_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, 
        kwargs={'block_id': B_1}, rounds=10) 

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.block.header_signature

def test_block_get_bad_request(benchmark):
    """Verifies requests for a specific block break with a bad protobuf.

    Expects to find:
        - a status of INTERNAL_ERROR
        - that the Block returned, when serialized, is empty
    """
    # response = self.make_bad_request(block_id=B_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_bad_request, setup=setUp2, 
        kwargs={'block_id': B_1}, rounds=10) 

    assert clientHanlerTestCase.status.INTERNAL_ERROR == response.status


def test_block_get_with_batch_id(benchmark):
    """Verifies requests for a block break properly with a batch id.

    Expects to find:
        - a status of NO_RESOURCE
        - that the Block returned, when serialized, is empty
    """
    # response = self.make_request(block_id=A_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, 
        kwargs={'block_id': A_1}, rounds=10) 

    assert clientHanlerTestCase.status.NO_RESOURCE == response.status



def setUp3():
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.BlockGetByTransactionRequest(store),
        client_block_pb2.ClientBlockGetByTransactionIdRequest,
        client_block_pb2.ClientBlockGetResponse)

def test_block_get_request(benchmark):
    """Verifies requests for a specific block by transaction work properly.

    Expects to find:
        - a status of OK
        - the block property which is an instances of Block
        - The block has a header_signature of 'bbb...1'
    """
    # response = self.make_request(transaction_id=C_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp3, 
        kwargs={'transaction_id': C_1}, rounds=10) 

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.block.header_signature



def setUp4():
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.BlockGetByBatchRequest(store),
        client_block_pb2.ClientBlockGetByBatchIdRequest,
        client_block_pb2.ClientBlockGetResponse)

def test_block_get_request(benchmark):
    """Verifies requests for a specific block by batch work properly.

    Expects to find:
        - a status of OK
        - the block property which is an instances of Block
        - The block has a header_signature of 'bbb...1'
    """
    # response = self.make_request(batch_id=A_1)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp4, 
        kwargs={'batch_id': A_1}, rounds=10) 

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.block.header_signature
