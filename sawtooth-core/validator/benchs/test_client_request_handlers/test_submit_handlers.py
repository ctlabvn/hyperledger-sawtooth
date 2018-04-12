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

from threading import Thread
from time import time, sleep

import sawtooth_validator.state.client_handlers as handlers
from sawtooth_validator.protobuf import client_batch_submit_pb2
from sawtooth_validator.protobuf.client_batch_submit_pb2 \
    import ClientBatchStatus
from test_client_request_handlers.base_case import ClientHandlerTestCase
from test_client_request_handlers.mocks import make_mock_batch
from test_client_request_handlers.mocks import make_store_and_tracker


A_0 = 'a' * 127 + '0'
A_1 = 'a' * 127 + '1'
A_2 = 'a' * 127 + '2'

clientHanlerTestCase = ClientHandlerTestCase()



def setUp():
    store, tracker = make_store_and_tracker()

    clientHanlerTestCase.initialize(
        handlers.BatchSubmitFinisher(tracker),
        client_batch_submit_pb2.ClientBatchSubmitRequest,
        client_batch_submit_pb2.ClientBatchSubmitResponse,
        store=store,
        tracker=tracker)

def test_batch_submit_without_wait(benchmark):
    """Verifies finisher simply returns OK when not set to wait.

    Expects to find:
        - a response status of OK
        - no batch_statuses
    """
    def batch_submit():
        setUp()
        batch_submit = client_batch_submit_pb2.ClientBatchSubmitRequest(batches=[make_mock_batch('new')])
        return clientHanlerTestCase._handle(batch_submit)

    
    # response = clientHanlerTestCase._handle(batch_submit)

    response = benchmark.pedantic(batch_submit, setup=setUp, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status



def setUp2():
    store, tracker = make_store_and_tracker()

    clientHanlerTestCase.initialize(
        handlers.BatchStatusRequest(tracker),
        client_batch_submit_pb2.ClientBatchStatusRequest,
        client_batch_submit_pb2.ClientBatchStatusResponse,
        store=store,
        tracker=tracker)

def test_batch_statuses_in_store(benchmark):
    """Verifies requests for status of a batch in the block store work.

    Queries the default mock block store with three blocks/batches:
        {
            header: {batch_ids: ['aaa...2'] ...},
             header_signature: 'bbb...2' ...}
        ,
        {
            header: {batch_ids: ['aaa...1'] ...},
             header_signature: 'bbb...1' ...}
        ,
        {
            header: {batch_ids: ['aaa...0'] ...},
             header_signature: 'bbb...0' ...
        }

    Expects to find:
        - a response status of OK
        - a status of COMMITTED at key '0' in batch_statuses
    """
    # response = clientHanlerTestCase.make_request(batch_ids=[A_0])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'batch_ids': [A_0]})

    assert clientHanlerTestCase.status.OK == response.status
    assert response.batch_statuses[0].batch_id == A_0
    assert response.batch_statuses[0].status == ClientBatchStatus.COMMITTED

    

def test_pending_batch_statuses(benchmark):
    """Verifies batch status requests marked PENDING by the tracker work.

    Queries the default mock batch tracker with pending batch ids of:
        - 'aaa...d'

    Expects to find:
        - a response status of OK
        - a status of PENDING at key 'aaa...d' in batch_statuses
    """
    # response = clientHanlerTestCase.make_request(batch_ids=['a' * 127 + 'd'])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'batch_ids': ['a' * 127 + 'd']})

    assert clientHanlerTestCase.status.OK == response.status
    assert response.batch_statuses[0].batch_id == 'a' * 127 + 'd'
    assert response.batch_statuses[0].status == ClientBatchStatus.PENDING




def test_batch_statuses_for_many_batches(benchmark):
    """Verifies requests for status of many batches work properly.

    Queries the default mock block store with three blocks/batches:
        {
            header: {batch_ids: ['aaa...2'] ...},
             header_signature: 'bbb...2' ...}
        ,
        {
            header: {batch_ids: ['aaa...1'] ...},
             header_signature: 'bbb...1' ...}
        ,
        {
            header: {batch_ids: ['aaa...0'] ...},
             header_signature: 'bbb...0' ...
        }

    ...and the default mock batch tracker with pending batch ids of:
        - 'aaa...d'

    Expects to find:
        - a response status of OK
        - a status of COMMITTED at key 'aaa...1' in batch_statuses
        - a status of COMMITTED at key 'aaa...2' in batch_statuses
        - a status of PENDING at key 'aaa...d' in batch_statuses
        - a status of UNKNOWN at key 'fff...f' in batch_statuses
    """
    # response = clientHanlerTestCase.make_request(
    #     batch_ids=[A_1, A_2, 'a' * 127 + 'd', 'f' * 128])

    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'batch_ids': [A_1, A_2, 'a' * 127 + 'd', 'f' * 128]})

    assert clientHanlerTestCase.status.OK == response.status
    assert response.batch_statuses[0].status == ClientBatchStatus.COMMITTED
    assert response.batch_statuses[1].status == ClientBatchStatus.COMMITTED
    assert response.batch_statuses[2].status == ClientBatchStatus.PENDING
    assert response.batch_statuses[3].status == ClientBatchStatus.UNKNOWN

def test_batch_statuses_with_wait(benchmark):
    """Verifies requests for status that wait for commit work properly.

    Queries the default mock block store which will have no block with
    the id 'aaa...e' until added by a separate thread.

    Expects to find:
        - less than 8 seconds to have passed (i.e. did not wait for
        timeout)
        - a response status of OK
        - a status of COMMITTED at key 'aaa...e' in batch_statuses
    """
    clientHanlerTestCase._tracker.notify_batch_pending(make_mock_batch('e'))
    start_time = time()

    def delayed_add():
        sleep(1)
        clientHanlerTestCase._store.add_block('e')
        clientHanlerTestCase._tracker.chain_update(None, [])

    Thread(target=delayed_add).start()

    # if there are more than 2 functions called, we can define a closure function then benchmark it
    # response = clientHanlerTestCase.make_request(
    #     batch_ids=['a' * 127 + 'e'],
    #     wait=True,
    #     timeout=10)

    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'batch_ids': ['a' * 127 + 'e'], 'wait': True, 'timeout': 10})

    assert 8 > time() - start_time
    assert clientHanlerTestCase.status.OK == response.status
    assert response.batch_statuses[0].status == ClientBatchStatus.UNKNOWN


def test_batch_statuses_with_committed_wait(benchmark):
    """Verifies requests for status that wait for commit work properly,
    when the batch is already committed.

    Expects to find:
        - less than 8 seconds to have passed (i.e. did not wait for
        timeout)
        - a response status of OK
        - a status of COMMITTED at key 'aaa...0' in batch_statuses
    """
    start_time = time()
    # response = clientHanlerTestCase.make_request(
    #     batch_ids=[A_0],
    #     wait=True,
    #     timeout=10)

    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'batch_ids': [A_0], 'wait': True, 'timeout': 10})

    assert 8 > time() - start_time
    assert clientHanlerTestCase.status.OK == response.status
    assert response.batch_statuses[0].status == ClientBatchStatus.COMMITTED
