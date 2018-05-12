import cProfile
import logging
import time
import random
import hashlib
import cbor


from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from test_completer.mock import MockGossip
from sawtooth_validator.journal.completer import Completer
from sawtooth_validator.database.dict_database import DictDatabase
from sawtooth_validator.journal.block_store import BlockStore
from sawtooth_validator.journal.block_wrapper import NULL_BLOCK_IDENTIFIER
from sawtooth_validator.protobuf.batch_pb2 import BatchHeader, Batch
from sawtooth_validator.protobuf.block_pb2 import BlockHeader, Block
from sawtooth_validator.protobuf.transaction_pb2 import TransactionHeader, Transaction


block_store = BlockStore(DictDatabase(
    indexes=BlockStore.create_index_configuration()))
gossip = MockGossip()
context = create_context('secp256k1')
crypto_factory = CryptoFactory(context)
private_key = context.new_random_private_key()
signer = crypto_factory.new_signer(private_key)
completer = Completer(block_store, gossip)


def _create_transactions(count, missing_dep=False):
    txn_list = []

    for _ in range(count):
        payload = {
            'Verb': 'set',
            'Name': 'name' + str(random.randint(0, 100)),
            'Value': random.randint(0, 100)
        }
        intkey_prefix = \
            hashlib.sha512('intkey'.encode('utf-8')).hexdigest()[0:6]

        addr = intkey_prefix + \
            hashlib.sha512(payload["Name"].encode('utf-8')).hexdigest()

        payload_encode = hashlib.sha512(cbor.dumps(payload)).hexdigest()

        header = TransactionHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            family_name='intkey',
            family_version='1.0',
            inputs=[addr],
            outputs=[addr],
            dependencies=[],
            batcher_public_key=signer.get_public_key().as_hex(),
            payload_sha512=payload_encode)

        if missing_dep:
            header.dependencies.extend(["Missing"])

        header_bytes = header.SerializeToString()

        signature = signer.sign(header_bytes)

        transaction = Transaction(
            header=header_bytes,
            payload=cbor.dumps(payload),
            header_signature=signature)

        txn_list.append(transaction)

    return txn_list


def _create_batches(batch_count, txn_count,
                    missing_dep=False):

    batch_list = []

    for _ in range(batch_count):
        txn_list = _create_transactions(txn_count,
                                        missing_dep=missing_dep)
        txn_sig_list = [txn.header_signature for txn in txn_list]

        batch_header = BatchHeader(
            signer_public_key=signer.get_public_key().as_hex())
        batch_header.transaction_ids.extend(txn_sig_list)

        header_bytes = batch_header.SerializeToString()

        signature = signer.sign(header_bytes)

        batch = Batch(
            header=header_bytes,
            transactions=txn_list,
            header_signature=signature)

        batch_list.append(batch)

    return batch_list


def _create_blocks(block_count,
                   batch_count,
                   missing_predecessor=False,
                   missing_batch=False,
                   find_batch=True):
    block_list = []

    for i in range(0, block_count):
        batch_list = _create_batches(batch_count, 2)
        batch_ids = [batch.header_signature for batch in batch_list]

        if missing_predecessor:
            predecessor = "Missing"
        else:
            predecessor = (block_list[i - 1].header_signature if i > 0 else
                           NULL_BLOCK_IDENTIFIER)

        block_header = BlockHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            batch_ids=batch_ids,
            block_num=i,
            previous_block_id=predecessor)

        header_bytes = block_header.SerializeToString()

        signature = signer.sign(header_bytes)

        if missing_batch:
            if find_batch:
                completer.add_batch(batch_list[-1])
            batch_list = batch_list[:-1]

        block = Block(
            header=header_bytes,
            batches=batch_list,
            header_signature=signature)

        block_list.append(block)

    return block_list


if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_completer.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    block = _create_blocks(1, 1)[0]

    pr.disable()
    pr.print_stats(sort='time')
