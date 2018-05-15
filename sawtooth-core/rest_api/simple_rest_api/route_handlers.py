# Copyright 2016, 2017 Intel Corporation
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

import asyncio
import re
import logging
import json
import base64
from aiohttp import web

# pylint: disable=too-many-lines

DEFAULT_TIMEOUT = 300
LOGGER = logging.getLogger(__name__)


class RouteHandler(object):

    def __init__(
            self, loop,
            timeout=DEFAULT_TIMEOUT):
        self._loop = loop        
        self._timeout = timeout
        

    async def fetch_state(self, request):

        address = request.match_info.get('address', '')                
        print('Received address: ' + address)
        return self._wrap_response(
            request,
            data={'address':address, 'data': 'eyJhc3NldCI6MTQxLCJvd25lciI6ImN4cGVsaCJ9'}
        )
        

    @staticmethod
    def _wrap_response(request, data=None, status=200):
        """Creates the JSON response envelope to be sent back to the client.
        """
        envelope = {}

        if data is not None:
            envelope['data'] = data

        return web.Response(
            status=status,
            content_type='application/json',
            text=json.dumps(
                envelope,
                indent=2,
                separators=(',', ': '),
                sort_keys=True))

    
