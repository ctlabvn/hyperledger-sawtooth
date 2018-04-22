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
import os
import shutil
import tempfile
import unittest
import struct

from sawtooth_validator.database.lmdb_nolock_database import  LMDBNoLockDatabase

def _serialize_tuple(tup):
    return "{}-{}-{}".format(*tup).encode()


def _deserialize_tuple(bytestring):
    (rec_id, name, data) = tuple(bytestring.decode().split('-'))
    return (int(rec_id), name, data)

db = LMDBNoLockDatabase(
            os.path.join('/tmp/sawtooth', 'nolock_db'),
            flag='c')

def do_put():
    db.put('1', (1, "foo", "bar"))
    db.put('2', (2, "alice", "Alice's data"))
    db.put('3', (3, "bob", "Bob's data"))  


def test_put(benchmark):
    """Test that a database with three records, plus an index will
    return the correct count of primary key/values, using `len`.
    """

    benchmark(do_put)


def test_get_multi(benchmark):
    """Given a database with three records and an index, test that it can
    return multiple values from a set of keys.

    Show that:
     - it returns all existing values in the list
     - ignores keys that do not exist (i.e. no error is thrown)
     - it works with index keys in the same manor
    """
    do_put()
    
    def do_get_multi():
        return db.get_multi(['3', '2'])
    

    multi_result = benchmark(do_get_multi)
    # get multi via the primary key, nolock return array instead of tupple
    assert multi_result == [
        ('3', [3, "bob", "Bob's data"]),
        ('2', [2, "alice", "Alice's data"])]
        


def test_delete(benchmark):
    """Test that items are deleted, including their index references.
    """
    do_put()


    benchmark(db.delete, '3')


def test_update(benchmark):
    """Test that a database will commit both inserts and deletes using the
    update method.
    """
    do_put()

    benchmark(db.update, [('4', (4, 'charlie', "Charlie's data"))], ['1'])
    assert ['2', '3', '4'] == db.keys()

