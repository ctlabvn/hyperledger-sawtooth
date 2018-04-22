# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import os
import pytest
import unittest
import random
import tempfile
from string import ascii_lowercase

from sawtooth_validator.state.merkle import MerkleDatabase
from sawtooth_validator.database import lmdb_nolock_database


def _hash(key):
    return MerkleDatabase.hash(key.encode())


def _random_string(length):
    return ''.join(random.choice(ascii_lowercase) for _ in range(length))

class TestSawtoothMerkleTrie:
    def __init__(self):
        self.dir = '/tmp/sawtooth' # tempfile.mkdtemp()
        self.file = os.path.join(self.dir, 'merkle.lmdb')

        self.lmdb = lmdb_nolock_database.LMDBNoLockDatabase(
            self.file,
            'n')

        self.trie = MerkleDatabase(self.lmdb)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.trie.close()
    

    # assertions
    def assert_value_at_address(self, address, value, ishash=False):
        assert self.get(address, ishash) == value            

    def assert_no_key(self, key):
        with pytest.raises(KeyError):
            self.get(key)

    def assert_root(self, expected):
        assert expected == self.get_merkle_root()
            

    def assert_not_root(self, *not_roots):
        root = self.get_merkle_root()
        for not_root in not_roots:
            assert root != not_root                

    # trie accessors

    # For convenience, assume keys are not hashed
    # unless otherwise indicated.

    def set(self, key, val, ishash=False):
        key_ = key if ishash else _hash(key)
        return self.trie.set(key_, val)

    def get(self, key, ishash=False):
        key_ = key if ishash else _hash(key)
        return self.trie.get(key_)

    def delete(self, key, ishash=False):
        key_ = key if ishash else _hash(key)
        return self.trie.delete(key_)

    def set_merkle_root(self, root):
        self.trie.set_merkle_root(root)

    def get_merkle_root(self):
        return self.trie.get_merkle_root()

    def update(self, set_items, delete_items=None, virtual=True):
        return self.trie.update(set_items, delete_items, virtual=virtual)




# def test_merkle_trie_root_advance(benchmark):
#     value = {'name': 'foo', 'value': 1}

#     @benchmark
#     def do_merkle_trie_root_advance():
#         with TestSawtoothMerkleTrie() as testSawtoothMerkleTrie:
#             orig_root = testSawtoothMerkleTrie.get_merkle_root()
#             new_root = testSawtoothMerkleTrie.set('foo', value)

#             testSawtoothMerkleTrie.assert_root(orig_root)
#             testSawtoothMerkleTrie.assert_no_key('foo')

#             testSawtoothMerkleTrie.set_merkle_root(new_root)

#             testSawtoothMerkleTrie.assert_root(new_root)
#             testSawtoothMerkleTrie.assert_value_at_address('foo', value)




# def test_merkle_trie_delete(benchmark):
#     value = {'name': 'bar', 'value': 1}
#     with TestSawtoothMerkleTrie() as testSawtoothMerkleTrie:

#         @benchmark
#         def do_merkle_trie_delete():
        
#             new_root = testSawtoothMerkleTrie.set('bar', value)
#             testSawtoothMerkleTrie.set_merkle_root(new_root)

#             testSawtoothMerkleTrie.assert_root(new_root)
#             testSawtoothMerkleTrie.assert_value_at_address('bar', value)

#             # deleting an invalid key should raise an error
#             with pytest.raises(KeyError):
#                 testSawtoothMerkleTrie.delete('barf')

#             del_root = testSawtoothMerkleTrie.delete('bar')

#             # del_root hasn't been set yet, so address should still have value
#             testSawtoothMerkleTrie.assert_root(new_root)
#             testSawtoothMerkleTrie.assert_value_at_address('bar', value)

#             testSawtoothMerkleTrie.set_merkle_root(del_root)

#             testSawtoothMerkleTrie.assert_root(del_root)
#             testSawtoothMerkleTrie.assert_no_key('bar')

def test_merkle_trie_update(benchmark):    
    with TestSawtoothMerkleTrie() as testSawtoothMerkleTrie:

        key = _random_string(10)
        hashed = _hash(key)
        value = {key: _random_string(512)}         
        # print(hashed, key)
        @benchmark
        def do_merkle_trie_update():
        
            # init_root = testSawtoothMerkleTrie.get_merkle_root()

            # values = {}
            # key_hashes = {
            #     key: _hash(key)
            #     for key in (_random_string(10) for _ in range(1))
            # }
            
            # for key, hashed in key_hashes.items():
                                               
            testSawtoothMerkleTrie.set(hashed, value, ishash=True)
                # values[hashed] = value
                # testSawtoothMerkleTrie.set_merkle_root(new_root)

        # custom benchmark
        # benchmark.pedantic(do_merkle_trie_update, iterations=1, rounds=1)

            # testSawtoothMerkleTrie.assert_not_root(init_root)

            # for address, value in values.items():
            #     testSawtoothMerkleTrie.assert_value_at_address(
            #         address, value, ishash=True)

            # set_items = {
            #     hashed: {
            #         key: 5.0
            #     }
            #     for key, hashed in random.sample(key_hashes.items(), 5)
            # }
            # values.update(set_items)
            # delete_items = {
            #     hashed
            #     for hashed in random.sample(list(key_hashes.values()), 5)
            # }

            # # make sure there are no sets and deletes of the same key
            # delete_items = delete_items - set_items.keys()
            # for addr in delete_items:
            #     del values[addr]

            # virtual_root = testSawtoothMerkleTrie.update(set_items, delete_items, virtual=True)

            # # virtual root shouldn't match actual contents of tree
            # with pytest.raises(KeyError):
            #     testSawtoothMerkleTrie.set_merkle_root(virtual_root)

            # actual_root = testSawtoothMerkleTrie.update(set_items, delete_items, virtual=False)

            # # the virtual root should be the same as the actual root
            # assert virtual_root == actual_root

            # # neither should be the root yet
            # testSawtoothMerkleTrie.assert_not_root(
            #     virtual_root,
            #     actual_root)

            # testSawtoothMerkleTrie.set_merkle_root(actual_root)
            # testSawtoothMerkleTrie.assert_root(actual_root)

            # for address, value in values.items():
            #     testSawtoothMerkleTrie.assert_value_at_address(
            #         address, value, ishash=True)

            # for address in delete_items:
            #     with pytest.raises(KeyError):
            #         testSawtoothMerkleTrie.get(address, ishash=True)


