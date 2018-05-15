import cProfile

import os
import shutil
import tempfile
import unittest
import struct

from sawtooth_validator.database.lmdb_nolock_database import LMDBNoLockDatabase


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


def test_get_multi():
    """Given a database with three records and an index, test that it can
    return multiple values from a set of keys.

    Show that:
     - it returns all existing values in the list
     - ignores keys that do not exist (i.e. no error is thrown)
     - it works with index keys in the same manor
    """
    do_put()

    db.get_multi(['3', '2'])
    # get multi via the primary key, nolock return array instead of tupple


def test_delete():
    """Test that items are deleted, including their index references.
    """
    do_put()
    db.delete('3')


def test_update():
    """Test that a database will commit both inserts and deletes using the
    update method.
    """
    do_put()
    db.update([('4', (4, 'charlie', "Charlie's data"))], ['1'])


if __name__ == '__main__':
    print("\n====== cProfile: nolock_db.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    test_update()
    test_get_multi()
    test_delete()

    pr.disable()
    pr.print_stats(sort='time')
