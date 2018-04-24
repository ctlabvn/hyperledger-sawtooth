
import cProfile

from unittest import mock
import tempfile
import os
from importlib import reload

from sawtooth_poet.poet_consensus import consensus_state
from sawtooth_poet.poet_consensus import consensus_state_store

from sawtooth_poet_common.protobuf.validator_registry_pb2 \
    import ValidatorInfo
from sawtooth_poet_common.protobuf.validator_registry_pb2 \
    import SignUpInfo
from sawtooth_poet.poet_consensus.consensus_state_store \
    import LMDBNoLockDatabase

class TestConsensusStateStore():
    def __init__(self):
        # pylint: disable=invalid-name,global-statement
        global consensus_state_store
        # Because ConsensusStateStore uses class variables to hold state
        # we need to reload the module after each test to clear state
        consensus_state_store = reload(consensus_state_store)


        self.dir = '/tmp/sawtooth' # tempfile.mkdtemp()
        self.file = os.path.join(self.dir, 'merkle.lmdb')

        self.lmdb = LMDBNoLockDatabase(
            self.file,
            'n')
        

    def assertEqual(self, value1, value2):
        # assert value1 == value2
        pass

    def assertTrue(self, value):
        # assert value == True
        pass



def do_consensus_store_set_get():
    """Verify that externally visible state (len, etc.) of the consensus
    state store after set is expected.  Verify that retrieving a
    previously set consensus state object results in the same values
    set.
    """
    # Make LMDB return empty dict

    testConsensusStateStore = TestConsensusStateStore()
    mock_lmdb = testConsensusStateStore.lmdb

    my_dict = {}
    mock_lmdb.return_value = my_dict

    mock_poet_settings_view = mock.Mock()
    mock_poet_settings_view.target_wait_time = 30.0
    mock_poet_settings_view.initial_wait_time = 3000.0
    mock_poet_settings_view.population_estimate_sample_size = 50

    store = \
        consensus_state_store.ConsensusStateStore(
            data_dir=tempfile.gettempdir(),
            validator_id='0123456789abcdef')
    

    # Store consensus state
    state = consensus_state.ConsensusState()
    store['key'] = state    

    # Retrieve the state and verify equality
    retrieved_state = store['key']

    testConsensusStateStore.assertEqual(
        state.aggregate_local_mean,
        retrieved_state.aggregate_local_mean)
    testConsensusStateStore.assertEqual(
        state.total_block_claim_count,
        retrieved_state.total_block_claim_count)

    # Have a validator claim a block and update the store
    wait_certificate = mock.Mock()
    wait_certificate.duration = 3.1415
    wait_certificate.local_mean = 5.0
    validator_info = \
        ValidatorInfo(
            id='validator_001',
            signup_info=SignUpInfo(
                poet_public_key='key_001'))
    state.validator_did_claim_block(
        validator_info=validator_info,
        wait_certificate=wait_certificate,
        poet_settings_view=mock_poet_settings_view)
    store['key'] = state

    # Verify the length and contains key
    testConsensusStateStore.assertEqual(len(store), 1)
    testConsensusStateStore.assertEqual(len(my_dict), 1)
    testConsensusStateStore.assertTrue('key' in store)
    testConsensusStateStore.assertTrue('key' in my_dict)

    # Retrieve the state and verify equality
    retrieved_state = store['key']

    testConsensusStateStore.assertEqual(
        state.aggregate_local_mean,
        retrieved_state.aggregate_local_mean)
    testConsensusStateStore.assertEqual(
        state.total_block_claim_count,
        retrieved_state.total_block_claim_count)

    validator_state = \
        retrieved_state.get_validator_state(
            validator_info=validator_info)
    retrieved_validator_state = \
        retrieved_state.get_validator_state(
            validator_info=validator_info)

    testConsensusStateStore.assertEqual(
        validator_state.key_block_claim_count,
        retrieved_validator_state.key_block_claim_count)
    testConsensusStateStore.assertEqual(
        validator_state.poet_public_key,
        retrieved_validator_state.poet_public_key)
    testConsensusStateStore.assertEqual(
        validator_state.total_block_claim_count,
        retrieved_validator_state.total_block_claim_count)

    # Delete the key and then verify length and does not contain key
    del store['key']
    testConsensusStateStore.assertEqual(len(store), 0)
    testConsensusStateStore.assertEqual(len(my_dict), 0)
    testConsensusStateStore.assertTrue('key' not in store)
    testConsensusStateStore.assertTrue('key' not in my_dict)

if __name__ == '__main__':
    print("\n====== cProfile: ./consensus/poet/core/cprofile_consensus_state_store.py ======\n")

    pr = cProfile.Profile()
    pr.enable()
    
    # temporary ignore
    # do_consensus_store_set_get()  

    pr.disable()
    pr.print_stats(sort='time')

