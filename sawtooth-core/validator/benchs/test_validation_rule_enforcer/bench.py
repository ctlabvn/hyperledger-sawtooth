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


def test_n_of_x(benchmark):
    """
    Test that if NofX Rule is set, the validation rule is checked
    correctly. Test:
        1. Valid Block, has one or less intkey transactions.
        2. Invalid Block, to many intkey transactions.
        3. Valid Block, ignore rule because it is formatted incorrectly.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()
    @benchmark
    def do_n_of_x():
        blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key")

        validationRuleEnforcerTest._settings_view_factory.add_setting(
            "sawtooth.validator.block_validation_rules",
            "NofX:0")

        assert enforce_validation_rules(
                validationRuleEnforcerTest._settings_view(),
                blkw.header.signer_public_key,
                blkw.batches) == True


def test_local(benchmark):
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
    @benchmark
    def do_local():

        blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key")

        validationRuleEnforcerTest._settings_view_factory.add_setting(
            "sawtooth.validator.block_validation_rules",
            "local:test")

        assert enforce_validation_rules(
                validationRuleEnforcerTest._settings_view(),
                blkw.header.signer_public_key,
                blkw.batches) == True

def test_all_at_once(benchmark):
    """
    Test that if multiple rules are set, they are all checked correctly.
    Block should be valid.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()
    @benchmark
    def do_all_at_once():
        blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key")
        validationRuleEnforcerTest._settings_view_factory.add_setting(
            "sawtooth.validator.block_validation_rules",
            "XatY:intkey,0;XatY:intkey,0;local:0")

        assert enforce_validation_rules(
                validationRuleEnforcerTest._settings_view(),
                blkw.header.signer_public_key,
                blkw.batches) == True


def test_all_at_once_signer_key(benchmark):
    """
    Test that if multiple rules are set, they are all checked correctly.
    Block is invalid, transaction at the 0th postion is not signed by the
    same signer as the block.
    """
    validationRuleEnforcerTest = ValidationRuleEnforcerTest()
    @benchmark
    def do_all_at_once_signer_key():
        blkw = validationRuleEnforcerTest._make_block(["intkey"], "pub_key", False)
        validationRuleEnforcerTest._settings_view_factory.add_setting(
            "sawtooth.validator.block_validation_rules",
            "XatY:intkey,0;XatY:intkey,0;local:0")

        assert enforce_validation_rules(
                validationRuleEnforcerTest._settings_view(),
                blkw.header.signer_public_key,
                blkw.batches) == False
