import cProfile

import time
import random

from sawtooth_block_info.processor.main import load_block_info_config
from sawtooth_block_info.processor.config.block_info import BlockInfoConfig
from sawtooth_block_info.common import create_block_address
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfo


#########################################################################################
VERBOSE_LEVEL = 1
DISTRIBUTION_NAME = 'sawadm'

BLOCKINFO_SIGNER_PUBLIC_KEY = "2" * 66
BLOCKINFO_HEADER_SIGNATURE = "1" * 128
BLOCKINFO_PREVIOUS_BLOCKID = "0" * 128
#########################################################################################


def do_test_create_block_info_config():
    blockInfoConfig = BlockInfoConfig()
    load_block_info_config(first_config = blockInfoConfig)

def do_test_common_create_block_address():
    block_num = random.randint(50000, 5000000)
    create_block_address(block_num = block_num)


if __name__ == '__main__':
    print("\n====== cProfile: ./families/block_info/cprof_families_blockinfo.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    do_test_create_block_info_config()
    do_test_common_create_block_address()

    pr.disable()
    pr.print_stats(sort='time')