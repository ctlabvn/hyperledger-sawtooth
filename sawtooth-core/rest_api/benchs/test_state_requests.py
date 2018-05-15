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

from base64 import b64decode
import asyncio
from aiohttp.test_utils import unittest_run_loop

from components import Mocks, BaseApiTest
from sawtooth_rest_api.protobuf.validator_pb2 import Message
from sawtooth_rest_api.protobuf import client_state_pb2
from sawtooth_rest_api.protobuf import client_block_pb2
from sawtooth_rest_api.protobuf import block_pb2


ID_A = 'a' * 128
ID_B = 'b' * 128
ID_C = 'c' * 128
ID_D = 'd' * 128

DEFAULT_LIMIT = 100
        


stateListTests = BaseApiTest()

stateListTests.loop = 10

stateListTests.set_status_and_connection(
            Message.CLIENT_STATE_LIST_REQUEST,
            client_state_pb2.ClientStateListRequest,
            client_state_pb2.ClientStateListResponse)

handlers = stateListTests.build_handlers(stateListTests.loop, stateListTests.connection)
stateListTests.build_app(stateListTests.loop, '/state', handlers.list_state)

async def test_state_list_with_address(time=100):
    """Verifies a GET /state works properly filtered by address.

    It will receive a Protobuf response with:
        - a head id of ID_C
        - an empty paging response
        - one leaf with addresses/data of: 'c': b'7'

    It should send a Protobuf request with:
        - an address property of 'c'
        - empty paging controls

    It should send back a JSON response with:
        - a response status of 200
        - a head property of ID_C
        - a link property that ends in
            '/state?head={}&start=c&limit=100&address=c'.format(ID_C)
        - a paging property that matches the paging response
        - a data property that is a list of 1 leaf dict
        - one leaf that matches the Protobuf response
    """
    paging = Mocks.make_paging_response("", "c", DEFAULT_LIMIT)
    entries = Mocks.make_entries(c=b'7')
    stateListTests.connection.preset_response(state_root='beef', paging=paging,
                                    entries=entries)
    stateListTests.connection.preset_response(
        proto=client_block_pb2.ClientBlockGetResponse,
        block=block_pb2.Block(
            header_signature=ID_C,
            header=block_pb2.BlockHeader(
                state_root_hash='beef').SerializeToString()))

    
    for _ in range(time):
        response = await stateListTests.get_assert_200('/state?address=c')
        print(response)
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()  
    loop.run_until_complete(test_state_list_with_address(10))  
    loop.close()      
