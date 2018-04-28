import cProfile
import logging
import time

from sawtooth_validator.journal.block_cache import BlockCache
from sawtooth_validator.journal.block_wrapper import BlockWrapper

from sawtooth_validator.protobuf.block_pb2 import Block
from sawtooth_validator.protobuf.block_pb2 import BlockHeader


def do_block_cache():
    block_store = {}
    cache = BlockCache(block_store=block_store, keep_time=1,
                       purge_frequency=1)

    header1 = BlockHeader(previous_block_id="000")
    block1 = BlockWrapper(Block(header=header1.SerializeToString(),
                                header_signature="ABC"))

    header2 = BlockHeader(previous_block_id="ABC")
    block2 = BlockWrapper(Block(header=header2.SerializeToString(),
                                header_signature="DEF"))

    header3 = BlockHeader(previous_block_id="BCA")
    block3 = BlockWrapper(Block(header=header3.SerializeToString(),
                                header_signature="FED"))

    cache[block1.header_signature] = block1
    cache[block2.header_signature] = block2

    return cache


if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_block_cache.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    do_block_cache()

    pr.disable()
    pr.print_stats(sort='time')