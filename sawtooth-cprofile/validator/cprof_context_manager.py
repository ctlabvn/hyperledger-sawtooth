import cProfile
import logging
import time
import hashlib


from sawtooth_validator.database import dict_database
from sawtooth_validator.execution import context_manager
from sawtooth_validator.state.merkle import MerkleDatabase


def _create_address(value=None):
    """
    Args:
        value: (str)

    Returns: (str) sha512 of value or random
    """
    if value is None:
        value = time.time().hex()
    return hashlib.sha512(value.encode()).hexdigest()[:70]


def _setup_context():

    database_of_record = dict_database.DictDatabase()
    ctx_mng = context_manager.ContextManager(database_of_record)
    first_state_hash = ctx_mng.get_first_root()

    # 1) Create transaction data
    first_transaction = {'inputs': [_create_address(a) for a in
                                    ['aaaa', 'bbbb', 'cccc']],
                            'outputs': [_create_address(a) for a in
                                        ['llaa', 'aall', 'nnnn']]}
    second_transaction = {
        'inputs': [_create_address(a) for a in
                    ['aaaa', 'dddd']],
        'outputs': [_create_address(a) for a in
                    ['zzzz', 'yyyy', 'tttt', 'qqqq']]
    }
    third_transaction = {
        'inputs': [_create_address(a) for a in
                    ['eeee', 'dddd', 'ffff']],
        'outputs': [_create_address(a) for a in
                    ['oooo', 'oozz', 'zzoo', 'ppoo', 'aeio']]
    }
    # 2) Create contexts based on that data
    context_id_1 = ctx_mng.create_context(
        state_hash= first_state_hash,
        base_contexts=[],
        inputs=first_transaction['inputs'],
        outputs=first_transaction['outputs'])
    context_id_2 = ctx_mng.create_context(
        state_hash= first_state_hash,
        base_contexts=[],
        inputs=second_transaction['inputs'],
        outputs=second_transaction['outputs'])
    context_id_3 = ctx_mng.create_context(
        state_hash= first_state_hash,
        base_contexts=[],
        inputs=third_transaction['inputs'],
        outputs=third_transaction['outputs'])

    # 3) Set addresses with values
    ctx_mng.set(context_id_1, [{_create_address(a): v}
                                            for a, v in [('llaa', b'1'),
                                                            ('aall', b'2'),
                                                            ('nnnn', b'3')]])
    ctx_mng.set(context_id_2, [{_create_address(a): v}
                                            for a, v in [('zzzz', b'9'),
                                                            ('yyyy', b'11'),
                                                            ('tttt', b'12'),
                                                            ('qqqq', b'13')]])
    ctx_mng.set(context_id_3, [{_create_address(a): v}
                                            for a, v in [('oooo', b'25'),
                                                            ('oozz', b'26'),
                                                            ('zzoo', b'27'),
                                                            ('ppoo', b'28'),
                                                            ('aeio', b'29')]])

    # 4)
    context_id = ctx_mng.create_context(
        state_hash= first_state_hash,
        base_contexts=[context_id_1, context_id_2, context_id_3],
        inputs=[
            _create_address(a)
            for a in ['llaa', 'yyyy', 'tttt', 'zzoo']
        ],
        outputs=[
            _create_address(a)
            for a in ['llaa', 'yyyy', 'tttt', 'zzoo', 'aeio']
        ])
    return context_id

if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_context_manager.py ======\n")
    pr = cProfile.Profile()
    pr.enable()
    
    _setup_context()

    pr.disable()
    pr.print_stats(sort='time')
