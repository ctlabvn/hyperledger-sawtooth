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

import math
import random
from unittest import TestCase
from unittest import mock

import cbor

from sawtooth_poet.poet_consensus import consensus_state

from sawtooth_poet_common.protobuf.validator_registry_pb2 \
    import ValidatorInfo

from sawtooth_poet_common.protobuf.validator_registry_pb2 \
    import SignUpInfo



MINIMUM_WAIT_TIME = 1.0

def test_get_missing_validator_state(benchmark):
    """Verify that retrieving missing validator state returns appropriate
    default values.
    """

    @benchmark
    def do_get_missing_validator_state():
        state = consensus_state.ConsensusState()

        # Try to get a non-existent validator ID and verify it returns default
        # value
        validator_info = \
            ValidatorInfo(
                id='validator_001',
                signup_info=SignUpInfo(
                    poet_public_key='key_001'))
        validator_state = \
            state.get_validator_state(validator_info=validator_info)

        assert validator_state.key_block_claim_count == 0
        assert validator_state.poet_public_key == 'key_001'
        assert validator_state.total_block_claim_count == 0


def test_validator_did_claim_block(benchmark):
    """Verify that trying to update consensus and validator state with
    validators that previous don't and do exist appropriately update the
    consensus and validator statistics.
    """
    @benchmark
    def do_validator_did_claim_block():
        state = consensus_state.ConsensusState()

        wait_certificate = mock.Mock()
        wait_certificate.duration = 3.1415
        wait_certificate.local_mean = 5.0

        poet_settings_view = mock.Mock()
        poet_settings_view.population_estimate_sample_size = 50

        validator_info = \
            ValidatorInfo(
                id='validator_001',
                signup_info=SignUpInfo(
                    poet_public_key='key_001'))

        # Have a non-existent validator claim a block, which should cause the
        # consensus state to add and set statistics appropriately.
        state.validator_did_claim_block(
            validator_info=validator_info,
            wait_certificate=wait_certificate,
            poet_settings_view=poet_settings_view)        

        validator_state = \
            state.get_validator_state(validator_info=validator_info)

        # Have the existing validator claim another block and verify that
        # the consensus and validator statistics are updated properly
        state.validator_did_claim_block(
            validator_info=validator_info,
            wait_certificate=wait_certificate,
            poet_settings_view=poet_settings_view)        

        validator_state = \
            state.get_validator_state(validator_info=validator_info)        

        # Have the existing validator claim another block, but with a new key,
        # and verify that the consensus and validator statistics are updated
        # properly
        validator_info.signup_info.poet_public_key = 'key_002'

        state.validator_did_claim_block(
            validator_info=validator_info,
            wait_certificate=wait_certificate,
            poet_settings_view=poet_settings_view)        

        validator_state = \
            state.get_validator_state(validator_info=validator_info)
        

def test_serialize(benchmark):
    """Verify that deserializing invalid data results in the appropriate
    error.  Verify that serializing state and then deserializing results
    in the same state values.
    """

    @benchmark
    def do_serialize():
        poet_settings_view = mock.Mock()
        poet_settings_view.population_estimate_sample_size = 50
       

        # Simple serialization of new consensus state and then deserialize
        # and compare
        state = consensus_state.ConsensusState()

        doppelganger_state = consensus_state.ConsensusState()
        doppelganger_state.parse_from_bytes(state.serialize_to_bytes())

        assert state.aggregate_local_mean == doppelganger_state.aggregate_local_mean
        