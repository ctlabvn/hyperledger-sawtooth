import cProfile
import unittest
import hashlib

import cbor

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_validator.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_validator.protobuf.transaction_pb2 import Transaction
from sawtooth_validator.protobuf.batch_pb2 import BatchHeader
from sawtooth_validator.protobuf.batch_pb2 import Batch
from sawtooth_validator.protobuf.block_pb2 import BlockHeader
from sawtooth_validator.protobuf.block_pb2 import Block
from sawtooth_validator.protobuf.events_pb2 import Event
from sawtooth_validator.protobuf.transaction_receipt_pb2 import \
    TransactionReceipt
from sawtooth_validator.journal.block_wrapper import BlockWrapper
from sawtooth_validator.gossip.permission_verifier import PermissionVerifier
from sawtooth_validator.gossip.permission_verifier import IdentityCache
from sawtooth_validator.gossip.identity_observer import IdentityObserver
from test_permission_verifier.mocks import MockIdentityViewFactory
from test_permission_verifier.mocks import make_policy


class TestPermissionVerifier():
    def __init__(self):
        context = create_context('secp256k1')
        crypto_factory = CryptoFactory(context)
        private_key = context.new_random_private_key()
        self.signer = crypto_factory.new_signer(private_key)
        self._identity_view_factory = MockIdentityViewFactory()
        self.permissions = {}
        self._identity_cache = IdentityCache(
            self._identity_view_factory)
        self.permission_verifier = \
            PermissionVerifier(
                permissions=self.permissions,
                current_root_func=self._current_root_func,
                identity_cache=self._identity_cache)

    @property
    def public_key(self):
        return self.signer.get_public_key().as_hex()

    def _current_root_func(self):
        return "0000000000000000000000"

    def _create_transactions(self, count):
        txn_list = []

        for _ in range(count):
            payload = {
                'Verb': 'set',
                'Name': 'name',
                'Value': 1,
            }

            intkey_prefix = \
                hashlib.sha512('intkey'.encode('utf-8')).hexdigest()[0:6]

            addr = intkey_prefix + \
                hashlib.sha512(payload["Name"].encode('utf-8')).hexdigest()

            payload_encode = hashlib.sha512(cbor.dumps(payload)).hexdigest()

            header = TransactionHeader(
                signer_public_key=self.public_key,
                family_name='intkey',
                family_version='1.0',
                inputs=[addr],
                outputs=[addr],
                dependencies=[],
                payload_sha512=payload_encode)

            header.batcher_public_key = self.public_key

            header_bytes = header.SerializeToString()

            signature = self.signer.sign(header_bytes)

            transaction = Transaction(
                header=header_bytes,
                payload=cbor.dumps(payload),
                header_signature=signature)

            txn_list.append(transaction)

        return txn_list

    def _create_batches(self, batch_count, txn_count):

        batch_list = []

        for _ in range(batch_count):
            txn_list = self._create_transactions(txn_count)
            txn_sig_list = [txn.header_signature for txn in txn_list]

            batch_header = BatchHeader(
                signer_public_key=self.signer.get_public_key().as_hex())
            batch_header.transaction_ids.extend(txn_sig_list)

            header_bytes = batch_header.SerializeToString()

            signature = self.signer.sign(header_bytes)

            batch = Batch(
                header=header_bytes,
                transactions=txn_list,
                header_signature=signature)

            batch_list.append(batch)

        return batch_list


def test_permission():
    """
    Test that if no roles are set and no default policy is set,
    permit all is used.
    """
    testPermissionVerifier = TestPermissionVerifier()

    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)


def test_default_policy_permission():
    """
    Test that if no roles are set, the default policy is used.
        1. Set default policy to permit all. Batch should be allowed.
        2. Set default policy to deny all. Batch should be rejected.
    """
    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy("default", [
        "PERMIT_KEY *"])
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy("default", [
        "DENY_KEY *"])
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)


def test_transactor_role():
    """
    Test that role:"transactor" is checked properly.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """

    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy("policy1", ["PERMIT_KEY " +
                                                                         testPermissionVerifier.public_key])
    testPermissionVerifier._identity_view_factory.add_role(
        "transactor", "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY other"])
    testPermissionVerifier._identity_view_factory.add_role(
        "transactor", "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)


def test_transactor_batch_signer():
    """
    Test that role: "transactor.batch_signer" is checked properly.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """

    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy("policy1", ["PERMIT_KEY " +
                                                                         testPermissionVerifier.public_key])
    testPermissionVerifier._identity_view_factory.add_role("transactor.batch_signer",
                                                           "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY other"])
    testPermissionVerifier._identity_view_factory.add_role("transactor.batch_signer",
                                                           "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)


def test_transactor_transaction_signer():
    """
    Test that role: "transactor.transaction_signer" is checked properly.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """
    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy("policy1", ["PERMIT_KEY " +
                                                                         testPermissionVerifier.public_key])
    testPermissionVerifier._identity_view_factory.add_role("transactor.transaction_signer",
                                                           "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY other"])
    testPermissionVerifier._identity_view_factory.add_role("transactor.transaction_signer",
                                                           "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)

# family intkey is like smartcontract


def test_transactor_transaction_siger_transaction_family():
    """
    Test that role: "transactor.transaction_signer.intkey" is checked
    properly.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """

    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy("policy1", ["PERMIT_KEY " +
                                                                         testPermissionVerifier.public_key])
    testPermissionVerifier._identity_view_factory.add_role(
        "transactor.transaction_signer.intkey",
        "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY other"])
    testPermissionVerifier._identity_view_factory.add_role(
        "transactor.transaction_signer.intkey",
        "policy1")
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.is_batch_signer_authorized(
        batch)


def test_off_chain_permissions():
    """
    Test that if permissions are empty all signers are permitted.
    """
    testPermissionVerifier = TestPermissionVerifier()

    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)


def test_off_chain_transactor():
    """
    Test that role:"transactor" is checked properly if in permissions.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """

    testPermissionVerifier = TestPermissionVerifier()

    policy = make_policy(
        "policy1", ["PERMIT_KEY " + testPermissionVerifier.public_key])
    testPermissionVerifier.permissions["transactor"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)

    policy = make_policy("policy1", ["PERMIT_KEY other"])
    testPermissionVerifier.permissions["transactor"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)


def test_off_chain_transactor_batch_signer():
    """
    Test that role:"transactor.batch_signer" is checked properly if in
    permissions.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """
    testPermissionVerifier = TestPermissionVerifier()

    policy = make_policy(
        "policy1", ["PERMIT_KEY " + testPermissionVerifier.public_key])
    testPermissionVerifier.permissions["transactor.batch_signer"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)

    policy = make_policy("policy1", ["PERMIT_KEY other"])
    testPermissionVerifier.permissions["transactor.batch_signer"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)


def test_off_chain_transactor_transaction_signer():
    """
    Test that role:"transactor.transaction_signer" is checked
    properly if in permissions.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.

    """
    testPermissionVerifier = TestPermissionVerifier()

    policy = make_policy(
        "policy1", ["PERMIT_KEY " + testPermissionVerifier.public_key])
    testPermissionVerifier.permissions["transactor.transaction_signer"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)

    policy = make_policy("policy1", ["PERMIT_KEY other"])
    testPermissionVerifier.permissions["transactor.transaction_signer"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)


def test_off_chain_transactor_transaction_signer_family():
    """
    Test that role:"transactor.transaction_signer.intkey" is checked
    properly if in permissions.
        1. Set policy to permit signing key. Batch should be allowed.
        2. Set policy to permit some other key. Batch should be rejected.
    """
    testPermissionVerifier = TestPermissionVerifier()

    policy = make_policy(
        "policy1", ["PERMIT_KEY " + testPermissionVerifier.public_key])
    testPermissionVerifier.permissions["transactor.transaction_signer.intkey"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)

    policy = make_policy("policy1", ["PERMIT_KEY other"])
    testPermissionVerifier.permissions["transactor.transaction_signer.intkey"] = policy
    batch = testPermissionVerifier._create_batches(1, 1)[0]
    allowed = testPermissionVerifier.permission_verifier.check_off_chain_batch_roles(
        batch)


def test_network():
    """
    Test that if no roles are set and no default policy is set,
    permit all is used.
    """
    testPermissionVerifier = TestPermissionVerifier()

    allowed = testPermissionVerifier.permission_verifier.check_network_role(
        testPermissionVerifier.public_key)


def test_network_consensus():
    """
    Test that if no roles are set and no default policy is set,
    permit all is used.
    """
    testPermissionVerifier = TestPermissionVerifier()

    allowed = testPermissionVerifier.permission_verifier.check_network_consensus_role(
        testPermissionVerifier.public_key)


def test_network_consensus_default():
    """
    Test that if no roles are set, the default policy is used.
        1. Set default policy to permit all. Public key should be allowed.
        2. Set default policy to deny all. Public key should be rejected.
    """
    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy("default", [
        "PERMIT_KEY *"])
    allowed = testPermissionVerifier.permission_verifier.check_network_consensus_role(
        testPermissionVerifier.public_key)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy("default", [
        "DENY_KEY *"])
    allowed = testPermissionVerifier.permission_verifier.check_network_consensus_role(
        testPermissionVerifier.public_key)


def test_network_consensus_role():
    """
    Test that role:"network.consensus" is checked properly.
        1. Set policy to permit signing key. Public key should be allowed.
        2. Set policy to permit some other key. Public key should be
            rejected.
    """
    testPermissionVerifier = TestPermissionVerifier()

    testPermissionVerifier._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY " + testPermissionVerifier.public_key])

    testPermissionVerifier._identity_view_factory.add_role(
        "network.consensus",
        "policy1")

    allowed = testPermissionVerifier.permission_verifier.check_network_consensus_role(
        testPermissionVerifier.public_key)

    testPermissionVerifier._identity_cache.forked()
    testPermissionVerifier._identity_view_factory.add_policy(
        "policy2", ["PERMIT_KEY other"])
    testPermissionVerifier._identity_view_factory.add_role(
        "network.consensus",
        "policy2")
    allowed = testPermissionVerifier.permission_verifier.check_network_consensus_role(
        testPermissionVerifier.public_key)


class TestIdentityObserver():
    def __init__(self):
        self._identity_view_factory = MockIdentityViewFactory()
        self._identity_cache = IdentityCache(
            self._identity_view_factory)
        self._identity_obsever = IdentityObserver(
            to_update=self._identity_cache.invalidate,
            forked=self._identity_cache.forked
        )

        # Make sure IdentityCache has populated roles and policy
        self._identity_view_factory.add_policy("policy1", ["PERMIT_KEY key"])
        self._identity_view_factory.add_role(
            "network",
            "policy1")
        self._identity_cache.get_role("network", "state_root")
        self._identity_cache.get_policy("policy1", "state_root")

    def _current_root_func(self):
        return "0000000000000000000000"

    def create_block(self, previous_block_id="0000000000000000"):
        block_header = BlockHeader(
            block_num=85,
            state_root_hash="0987654321fedcba",
            previous_block_id=previous_block_id)
        block = BlockWrapper(
            Block(
                header_signature="abcdef1234567890",
                header=block_header.SerializeToString()))
        return block


def test_chain_update():
    """
    Test that if there is no fork and only one value is udpated, only
    that value is in validated in the catch.
    """
    # Set up cache so it does not fork

    testIdentityObserver = TestIdentityObserver()

    block1 = testIdentityObserver.create_block()
    testIdentityObserver._identity_obsever.chain_update(block1, [])
    testIdentityObserver._identity_cache.get_role("network", "state_root")
    testIdentityObserver._identity_cache.get_policy(
        "policy1", "state_root")

    # Add next block and event that says network was updated.
    block2 = testIdentityObserver.create_block("abcdef1234567890")
    event = Event(
        event_type="identity/update",
        attributes=[Event.Attribute(key="updated", value="network")])
    receipts = TransactionReceipt(events=[event])
    testIdentityObserver._identity_obsever.chain_update(block2, [receipts])

    identity_view = \
        testIdentityObserver._identity_view_factory.create_identity_view(
            "state_root")


def test_fork():
    """
    Test that if there is a fork, all values in the cache will be
    invalidated and fetched from state.
    """
    testIdentityObserver = TestIdentityObserver()

    block = testIdentityObserver.create_block()
    testIdentityObserver._identity_obsever.chain_update(block, [])


class TestIdentityCache():
    def __init__(self):
        self._identity_view_factory = MockIdentityViewFactory()
        self._identity_cache = IdentityCache(
            self._identity_view_factory)


def test_get_role():
    """
    Test that a role can be fetched from the state.
    """
    testIdentityCache = TestIdentityCache()

    testIdentityCache._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY key"])
    testIdentityCache._identity_view_factory.add_role(
        "network",
        "policy1")


def test_get_policy():
    """
    Test that a policy can be fetched from the state.
    """
    testIdentityCache = TestIdentityCache()

    testIdentityCache._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY key"])
    testIdentityCache._identity_view_factory.add_role(
        "network",
        "policy1")


def test_role_invalidate():
    """
    Test that a role can be invalidated.
    """
    testIdentityCache = TestIdentityCache()

    testIdentityCache._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY key"])
    testIdentityCache._identity_view_factory.add_role(
        "network",
        "policy1")
    testIdentityCache._identity_cache.invalidate("network")


def test_forked():
    """
    Test that forked() invalidates all items in the cache, and they can
    be fetched from state.
    """
    testIdentityCache = TestIdentityCache()

    testIdentityCache._identity_view_factory.add_policy(
        "policy1", ["PERMIT_KEY key"])
    testIdentityCache._identity_view_factory.add_role(
        "network",
        "policy1")

    identity_view = \
        testIdentityCache._identity_view_factory.create_identity_view(
            "state_root")

    testIdentityCache._identity_cache.get_policy("policy1", "state_root")
    testIdentityCache._identity_cache.get_role("network", "state_root")


if __name__ == '__main__':
    print("\n====== cProfile: permission_verifier.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    test_permission()
    test_default_policy_permission()
    test_transactor_role()
    test_transactor_batch_signer()
    test_transactor_transaction_signer()
    test_transactor_transaction_siger_transaction_family()
    test_off_chain_permissions()
    test_off_chain_transactor()
    test_off_chain_transactor_batch_signer()
    test_off_chain_transactor_transaction_signer()
    test_off_chain_transactor_transaction_signer_family()
    test_network()
    test_network_consensus()
    test_network_consensus_default()
    test_network_consensus_role()
    test_chain_update()
    test_fork()
    test_get_role()
    test_get_policy()
    test_role_invalidate()
    test_forked()

    pr.disable()
    pr.print_stats(sort='time')
