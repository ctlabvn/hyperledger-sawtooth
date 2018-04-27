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

import collections
import logging
import os
import toml

LOGGER = logging.getLogger(__name__)


class RestApiConfig:
    def __init__(
            self,
            bind=None,            
            timeout=None):
        self._bind = bind        
        self._timeout = timeout

    @property
    def bind(self):
        return self._bind    

    @property
    def timeout(self):
        return self._timeout    

    def __repr__(self):
        # skip opentsdb_db password
        return \
            "{}(bind={}, timeout={}," \
            .format(
                self.__class__.__name__,
                repr(self._bind),
                repr(self._timeout))

    def to_dict(self):
        return collections.OrderedDict([
            ('bind', self._bind),
            ('timeout', self._timeout),
        ])

    def to_toml_string(self):
        return str(toml.dumps(self.to_dict())).strip().split('\n')
