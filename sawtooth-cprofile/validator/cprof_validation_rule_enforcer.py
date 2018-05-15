import cProfile
import unittest

from sawtooth_validator.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_validator.protobuf.transaction_pb2 import Transaction
from sawtooth_validator.protobuf.batch_pb2 import Batch
from sawtooth_validator.protobuf.block_pb2 import BlockHeader
from sawtooth_validator.protobuf.block_pb2 import Block
from sawtooth_validator.journal.block_wrapper import BlockWrapper
from sawtooth_validator.journal.validation_rule_enforcer import \
    enforce_validation_rules
from test_validation_rule_enforcer.mock import MockSettingsViewFactory


class ValidationRuleEnforcerTest():
    def __init__(self):
        self._settings_view_factory = MockSettingsViewFactory()

    def _settings_view(self):
        return self._settings_view_factory.create_settings_view(
            "state_root")

    def _make_block(self, txns_family, signer_public_key,
                    same_public_key=True):
        transactions = []
        for family in txns_family:
            txn_header = TransactionHeader(
                family_name=family,
                signer_public_key=signer_public_key)
            txn = Transaction(header=txn_header.SerializeToString())
            transactions.append(txn)

        batch = Batch(transactions=transactions)
        if same_public_key:
            block_header = BlockHeader(signer_public_key=signer_public_key)
        else:
            block_header = BlockHeader(signer_public_key="other")
        block = Block(header=block_header.SerializeToString(), batches=[batch])
        return BlockWrapper(block)


def test_n_of_x():
    """
    Test that if NofX Rule is set, the validation rule is checked
    correctly. Test:
        1. Valid Block, has one or less intkey transactions.
        2. Invalid Block, to many intkey transactions.
        3. Valid Block, ignore rule because it is formatted incorrectly.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()

    blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key")

    validationRuleEnforcerTest._settings_view_factory.add_setting(
        "sawtooth.validator.block_validation_rules",
        "NofX:0")


def test_local():
    """
    Test that if local Rule is set, the validation rule is checked
    correctly. Test:
        1. Valid Block, first transaction is signed by the same signer as
           the block.
        2. Invalid Block, first transaction is not signed by the same
           signer as the block.
        3. Valid Block, ignore rule because it is formatted incorrectly.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()

    blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key")

    validationRuleEnforcerTest._settings_view_factory.add_setting(
        "sawtooth.validator.block_validation_rules",
        "local:test")


def test_all_at_once():
    """
    Test that if multiple rules are set, they are all checked correctly.
    Block should be valid.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()

    blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key")
    validationRuleEnforcerTest._settings_view_factory.add_setting(
        "sawtooth.validator.block_validation_rules",
        "XatY:intkey,0;XatY:intkey,0;local:0")


def test_all_at_once_signer_key():
    """
    Test that if multiple rules are set, they are all checked correctly.
    Block is invalid, transaction at the 0th postion is not signed by the
    same signer as the block.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()

    blkw = validationRuleEnforcerTest._make_block(
        ["intkey"], "pub_key", False)
    validationRuleEnforcerTest._settings_view_factory.add_setting(
        "sawtooth.validator.block_validation_rules",
        "XatY:intkey,0;XatY:intkey,0;local:0")


if __name__ == '__main__':
    print("\n====== cProfile: validation_rule_enforcer.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    test_n_of_x()
    test_local()
    test_all_at_once()
    test_all_at_once_signer_key()

    pr.disable()
    pr.print_stats(sort='time')
