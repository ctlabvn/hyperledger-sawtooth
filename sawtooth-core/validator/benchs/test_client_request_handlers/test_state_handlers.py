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
from sawtooth_validator.protobuf import client_state_pb2
from test_client_request_handlers.base_case import ClientHandlerTestCase
from test_client_request_handlers.mocks import make_db_and_store


clientHanlerTestCase = ClientHandlerTestCase()


def _find_value(entries, address):
    """The ordering of entries is fairly arbitrary, so some tests
    need to filter for the matching address.
    """
    return [l for l in entries if l.address == address][0].data

def setUp():
    db, store, roots = make_db_and_store()
    clientHanlerTestCase.initialize(
        handlers.StateListRequest(db, store),
        client_state_pb2.ClientStateListRequest,
        client_state_pb2.ClientStateListResponse,
        store=store,
        roots=roots)

def test_state_list_request(benchmark):
    """Verifies requests for data lists without parameters work properly.

    Queries the latest state in the default mock db:
        state: {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    the tests expect to find:
        - a status of OK
        - the latest state_root
        - a paging response with start of b'3' and limit 100
        - a list of entries with 3 items
        - that the list contains instances of ClientStateListResponse.Entry
        - that there is a leaf with an address of '00..1' and data of b'3'
    """
    # response = clientHanlerTestCase.make_request()
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10)

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root
    assert 3 == len(response.entries)    
    assert b'3' == _find_value(response.entries, '0' * 69 + '1')


def test_state_list_with_root(benchmark):
    """Verifies requests for data lists work properly with a merkle root.

    Queries the first state in the default mock db:
        {'00..1': b'1'}

    Expects to find:
        - a status of OK
        - that state_root is missing (queried by root)
        - a paging response with start of b'1' and limit 100
        - a list of entries with 1 item
        - that the list contains instances of ClientStateListResponse.Entry
        - that ClientStateListResponse.Entry has an address of '00..1' and
          data of b'1'
    """
    # response = clientHanlerTestCase.make_request(state_root=clientHanlerTestCase.roots[0])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'state_root':clientHanlerTestCase.roots[0]})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[0] == response.state_root
    assert 1 == len(response.entries)
    assert '0' * 69 + '1' == response.entries[0].address
    assert b'1' == response.entries[0].data


def test_state_list_with_address(benchmark):
    """Verifies requests for data lists filtered by address work properly.

    Queries the latest state in the default mock db:
        {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    Expects to find:
        - a status of OK
        - the latest state_root
        - a paging response with start of b'7' and limit 100
        - a list of entries with 1 item
        - that the list contains instances of ClientStateListResponse.Entry
        - that ClientStateListResponse.Entry matches the address of '00..3'
          and has data of b'7'
    """
    # response = clientHanlerTestCase.make_request(address='0' * 69 + '3')
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'address':'0' * 69 + '3'})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root
    assert 1 == len(response.entries)
    assert '0' * 69 + '3' == response.entries[0].address
    assert b'7' == response.entries[0].data


def test_state_list_with_head_and_address(benchmark):
    """Verifies requests for data work with a head and address filter.

    Queries the second state in the default mock db:
        {'00..1': b'2', '00..2': b'4'}

    Expects to find:
        - a status of OK
        - the state_root from block 'bbb...1'
        - a paging response with start of b'4' and limit 100
        - a list of entries with 1 item
        - that the list contains instances of
          ClientStateListResponse.Entry
        - that ClientStateListResponse.Entry matches the address
          of '00..2', and has data of b'4'

    """
    # response = clientHanlerTestCase.make_request(
    #     state_root=clientHanlerTestCase.roots[1], address='0' * 69 + '2')
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'state_root': clientHanlerTestCase.roots[1], 'address':'0' * 69 + '2'})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[1] == response.state_root
    assert 1 == len(response.entries)
    assert '0' * 69 + '2' == response.entries[0].address
    assert b'4' == response.entries[0].data

def test_state_list_with_early_state(benchmark):
    """Verifies requests for data break when the state predates an address.

    Attempts to query the second state in the default mock db:
        {'00..1': b'2', '00..2': b'4'}

    Expects to find:
        - a status of NO_RESOURCE
        - the state_root from block 'bbb...1'
        - that paging and entries are missing
    """
    # response = clientHanlerTestCase.make_request(
    #     address='0' * 69 + '3', state_root=clientHanlerTestCase.roots[1])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'state_root': clientHanlerTestCase.roots[1], 'address':'0' * 69 + '3'})

    assert clientHanlerTestCase.status.NO_RESOURCE == response.status
    assert clientHanlerTestCase.roots[1] == response.state_root

def test_state_list_paginated(benchmark):
    """Verifies requests for data lists work when paginated just by limit.

    Queries the latest state in the default mock db:
        {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    Expects to find:
        - a status of OK
        - the latest state_root
        - a paging response with a next_id of '00..3', start '00..1', and
          limit '2'
        - a list of entries with 2 items
        - those items are instances of ClientStateListResponse.Entry
    """
    # response = clientHanlerTestCase.make_paged_request(limit=2)
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 2})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root    
    assert 2 == len(response.entries)

def test_state_list_paginated_by_start_id(benchmark):
    """Verifies data list requests work paginated by limit and start_id.

    Queries the latest state in the default mock db:
        {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    Expects to find:
        - a status of OK
        - the latest state_root
        - a paging response with:
            * limit 1
            * start of '00..2'
            * a next_id of '00..3'
        - a list of entries with 1 item
        - that item is an instance of ClientStateListResponse.Entry
        - that ClientStateListResponse.Entry has an address of '00..2' and
          data of b'5'
    """
    # response = clientHanlerTestCase.make_paged_request(limit=1, start='0' * 69 + '2')
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 1, 'start':'0' * 69 + '2'})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root
    assert 1 == len(response.entries)
    assert '0' * 69 + '2' == response.entries[0].address
    assert b'5' == response.entries[0].data



def test_state_list_paginated_with_state_root(benchmark):
    """Verifies data list requests work with both paging and a head id.

    Queries the second state in the default mock db:
        {'00..1': b'2', '00..2': b'4'}

    Expects to find:
        - a status of OK
        - the state_root of block 'bbb...1'
        - a paging response with a next_id of '00..1', start '00..2', and
          limit '2'
        - a list of entries with 1 item
        - that item is an instance of ClientStateListResponse.Entry
        - that ClientStateListResponse.Entry has an address of '00..2' and
          data of b'4'
    """
    # response = clientHanlerTestCase.make_paged_request(
    #     limit=1, start="0" * 69 + '2', state_root=clientHanlerTestCase.roots[1])

    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 1, 'start':'0' * 69 + '2', 'state_root': clientHanlerTestCase.roots[1]})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[1] == response.state_root
    assert 1 == len(response.entries)
    assert '0' * 69 + '2' == response.entries[0].address
    assert b'4' == response.entries[0].data

def test_state_list_paginated_with_address(benchmark):
    """Verifies data list requests work with both paging and an address.

    Queries the latest state in the default mock db:
        {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    Expects to find:
        - a status of OK
        - the latest state_root
    - the default empty paging response
        - a list of entries with 1 item
        - that item is an instance of ClientStateListResponse.Entry
        - that ClientStateListResponse.Entry has an address of '00..2' and
          data of b'5'
    """
    # response = clientHanlerTestCase.make_paged_request(limit=1, address='0' * 69 + '2')
    response = benchmark.pedantic(clientHanlerTestCase.make_paged_request, setup=setUp, rounds=10,
        kwargs={'limit': 1, 'address':'0' * 69 + '2'})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root
    assert 1 == len(response.entries)
    assert '0' * 69 + '2' == response.entries[0].address
    assert b'5' == response.entries[0].data

def test_state_list_sorted_in_reverse(benchmark):
    """Verifies data list requests work sorted by a key in reverse.

    Queries the latest state in the default mock db:
        {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    Expects to find:
        - a status of OK
        - the latest state_root
        - a paging response with a next_id of '00..3' and a limit of 100
        - a list of entries with 3 items
        - the items are instances of ClientStateListResponse.Entry
        - the first ClientStateListResponse.Entry has an address of '00..3'
          and data of b'7'
        - the last ClientStateListResponse.Entry has an address of '00..1'
          and data of b'3'
    """
    controls = clientHanlerTestCase.make_sort_controls('default', reverse=True)
    # response = clientHanlerTestCase.make_request(sorting=controls)
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp, rounds=10,
        kwargs={'sorting': controls})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root
    assert 3 == len(response.entries)
    assert '0' * 69 + '3' == response.entries[0].address
    assert b'7' == response.entries[0].data
    assert '0' * 69 + '1' == response.entries[2].address
    assert b'3' == response.entries[2].data

# benchmark scenario 2

def setUp2():
    db, store, roots = make_db_and_store()
    clientHanlerTestCase.initialize(
        handlers.StateGetRequest(db, store),
        client_state_pb2.ClientStateGetRequest,
        client_state_pb2.ClientStateGetResponse,
        store=store,
        roots=roots)

def test_state_get_request(benchmark):
    """Verifies requests for specific data by address work properly.

    Queries the latest state in the default mock db:
        {'00...1': b'3', '00...2': b'5', '00...3': b'7'}

    Expects to find:
        - a status of OK
        - the latest state_root
        - a value of b'5'
    """
    # response = clientHanlerTestCase.make_request(address='0' * 69 + '2')
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'address': '0' * 69 + '2'})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[2] == response.state_root
    assert b'5' == response.value

def test_state_get_with_root(benchmark):
    """Verifies requests for specific data work with a merkle root.

    Queries the second state in the default mock db:
        {'00..1': b'2', '00..2': b'4'}

    Expects to find:
        - a status of OK
        - that state_root is missing (queried by root)
        - a value of b'4'
    """
    # response = clientHanlerTestCase.make_request(
    #     address='0' * 69 + '2', state_root=clientHanlerTestCase.roots[1])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'address': '0' * 69 + '2', 'state_root': clientHanlerTestCase.roots[1]})

    assert clientHanlerTestCase.status.OK == response.status
    assert clientHanlerTestCase.roots[1] == response.state_root
    assert b'4' == response.value


def test_state_get_with_early_state(benchmark):
    """Verifies requests for a datum break when state predates the address.

    Attempts to query the second state in the default mock db:
        {'00..1': b'2', '00..2': b'4'}

    Expects to find:
        - a status of NO_RESOURCE
        - that value and state_root are missing
    """
    # response = clientHanlerTestCase.make_request(
    #     address='0' * 69 + '3', state_root=clientHanlerTestCase.roots[1])
    response = benchmark.pedantic(clientHanlerTestCase.make_request, setup=setUp2, rounds=10,
        kwargs={'address': '0' * 69 + '3', 'state_root': clientHanlerTestCase.roots[1]})

    assert clientHanlerTestCase.status.NO_RESOURCE == response.status
