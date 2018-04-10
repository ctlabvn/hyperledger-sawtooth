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
from sawtooth_validator.protobuf import client_batch_pb2
from sawtooth_validator.protobuf.batch_pb2 import Batch
from test_client_request_handlers.base_case import ClientHandlerTestCase
from test_client_request_handlers.mocks import MockBlockStore


B_0 = 'b' * 127 + '0'
B_1 = 'b' * 127 + '1'
B_2 = 'b' * 127 + '2'
A_0 = 'a' * 127 + '0'
A_1 = 'a' * 127 + '1'
A_2 = 'a' * 127 + '2'


clientHanlerTestCase = ClientHandlerTestCase()

def setUp():    
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.BatchListRequest(store),
        client_batch_pb2.ClientBatchListRequest,
        client_batch_pb2.ClientBatchListResponse,
        store=store)



def test_batch_list_request(benchmark):
    """Verifies requests for batch lists without parameters work properly.

    Queries the default mock block store with three blocks:
        {
            header_signature: 'bbb...2',
             batches: [{header_signature: 'aaa...2' ...}] ...
        }
        {
            header_signature: 'bbb...1',
             batches: [{header_signature: 'aaa...1' ...}] ...
        }
        {
            header_signature: 'bbb...0',
             batches: [{header_signature: 'aaa...0' ...}] ...
        }

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...2' (the latest)
        - a paging response with a start of A_2 and 100
        - a list of batches with 3 items
        - the items are instances of Batch
        - the first item has a header_signature of 'aaa...2'
    """
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_2 == response.head_id
    assert 3 == len(response.batches)
    assert A_2 == response.batches[0].header_signature





def test_batch_list_with_head(benchmark):
    """Verifies requests for lists of batches work properly with a head id.

    Queries the default mock block store with '1' as the head:
        {
            header_signature: 'bbb...1',
             batches: [{header_signature: 'aaa...1' ...}] ...
        }
        {
            header_signature: 'bbb...0',
             batches: [{header_signature: 'aaa...0' ...}] ...
        }

    Expects to find:
        - a status of OK
        - a head_id of 'bbb...1'
        - a paging response with start of A_1 and limit 100
        - a list of batches with 2 items
        - the items are instances of Batch
        - the first item has a header_signature of 'aaa...1'
    """
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, 
        kwargs={'head_id':B_1}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert B_1 == response.head_id
    assert 2 == len(response.batches)
    assert A_1 == response.batches[0].header_signature


def setUp2():
    store = MockBlockStore()
    clientHanlerTestCase.initialize(
        handlers.BatchGetRequest(store),
        client_batch_pb2.ClientBatchGetRequest,
        client_batch_pb2.ClientBatchGetResponse,
        store=store)

def test_batch_get_request(benchmark):
    """Verifies requests for a specific batch by id work properly.

    Queries the default three block mock store for a batch id of 'aaa...1'.
    Expects to find:
        - a status of OK
        - a batch property which is an instances of Batch
        - the batch has a header_signature of 'aaa...1'
    """
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, 
        kwargs={'batch_id':A_1}, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert A_1 == response.batch.header_signature

   

def test_batch_get_with_block_id(benchmark):
    """Verifies requests for a batch break properly with a block id.

    Expects to find:
        - a status of NO_RESOURCE
        - that the Batch returned, when serialized, is actually empty
    """
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, 
        kwargs={'batch_id':B_1}, rounds=10)

    assert clientHanlerTestCase.status.NO_RESOURCE == response.status
