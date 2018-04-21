import cProfile
from unittest import mock

from sawtooth_poet.poet_consensus import consensus_state
from sawtooth_poet_common.protobuf.validator_registry_pb2 \
    import ValidatorInfo
from sawtooth_poet_common.protobuf.validator_registry_pb2 \
    import SignUpInfo

MINIMUM_WAIT_TIME = 1.0

def do_get_missing_validator_state():
    """Verify that retrieving missing validator state returns appropriate
    default values.
    """
    state = consensus_state.ConsensusState()

    # Try to get a non-existent validator ID and verify it returns default
    # value
    validator_info = \
        ValidatorInfo(
            id='validator_001',
            signup_info=SignUpInfo(
                poet_public_key='key_001'))
    validator_state = state.get_validator_state(validator_info=validator_info)

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
if __name__ == '__main__':
    print("\n====== cProfile: ./consensus/poet/common/cprof_consensus_sate.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    do_get_missing_validator_state()
    do_validator_did_claim_block()

    pr.disable()
    pr.print_stats(sort='time')