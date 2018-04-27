
import os
import cProfile

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from sawtooth_validator.networking.handlers import AuthorizationChallengeRequestHandler
from sawtooth_validator.networking.handlers import AuthorizationChallengeSubmitHandler

from sawtooth_validator.protobuf.authorization_pb2 import ConnectionRequest
from sawtooth_validator.protobuf.authorization_pb2 import RoleType
from test_authorization_handlers.mock import MockNetwork
from sawtooth_validator.networking.interconnect import AuthorizationType
from sawtooth_validator.networking.interconnect import ConnectionStatus
from sawtooth_validator.networking.handlers import ConnectHandler
from sawtooth_validator.networking.handlers import AuthorizationTrustRequestHandler
from sawtooth_validator.protobuf.authorization_pb2 import AuthorizationTrustRequest
from sawtooth_validator.protobuf.authorization_pb2 import AuthorizationChallengeRequest
from sawtooth_validator.protobuf.authorization_pb2 import AuthorizationChallengeSubmit

from test_authorization_handlers.mock import MockPermissionVerifier
from test_authorization_handlers.mock import MockGossip

def do_connect():
    connect_message = ConnectionRequest(endpoint="endpoint")
    roles = {"network": AuthorizationType.TRUST}
    network = MockNetwork(roles)
    handler = ConnectHandler(network)
    handler_status = handler.handle("connection_id",
                                    connect_message.SerializeToString())
    return handler_status


def do_authorization_trust_request():
    """
    Test the AuthorizationTrustRequestHandler returns an
    AuthorizationTrustResponse if the AuthorizationTrustRequest should be
    approved.
    """
    auth_trust_request = AuthorizationTrustRequest(
        roles=[RoleType.Value("NETWORK")],
        public_key="public_key")

    roles = {"network": AuthorizationType.TRUST}

    network = MockNetwork(
        roles,
        connection_status={"connection_id":
                           ConnectionStatus.CONNECTION_REQUEST})
    permission_verifer = MockPermissionVerifier()
    gossip = MockGossip()
    handler = AuthorizationTrustRequestHandler(
        network, permission_verifer, gossip)
    handler_status = handler.handle(
        "connection_id",
        auth_trust_request.SerializeToString())

    return handler_status


def do_authorization_challenge_request():
    """
    Test the AuthorizationChallengeRequestHandler returns an
    AuthorizationChallengeResponse.
    """
    auth_challenge_request = AuthorizationChallengeRequest()
    roles = {"network": AuthorizationType.TRUST}

    network = MockNetwork(
        roles,
        connection_status={
            "connection_id": ConnectionStatus.CONNECTION_REQUEST
        })
    handler = AuthorizationChallengeRequestHandler(network)
    handler_status = handler.handle(
        "connection_id",
        auth_challenge_request.SerializeToString())

    return handler_status

def do_authorization_challenge_submit():
    """
    Test the AuthorizationChallengeSubmitHandler returns an
    AuthorizationChallengeResult.
    """
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    crypto_factory = CryptoFactory(context)
    signer = crypto_factory.new_signer(private_key)

    payload = os.urandom(10)

    signature = signer.sign(payload)

    auth_challenge_submit = AuthorizationChallengeSubmit(
        public_key=signer.get_public_key().as_hex(),
        signature=signature,
        roles=[RoleType.Value("NETWORK")])

    roles = {"network": AuthorizationType.TRUST}

    network = MockNetwork(
        roles,
        connection_status={
            "connection_id": ConnectionStatus.AUTH_CHALLENGE_REQUEST
        })
    permission_verifer = MockPermissionVerifier()
    gossip = MockGossip()
    handler = AuthorizationChallengeSubmitHandler(
        network, permission_verifer, gossip, {"connection_id": payload})
    handler_status = handler.handle(
        "connection_id",
        auth_challenge_submit.SerializeToString())

    return handler_status 

if __name__ == '__main__':
    print("\n====== cProfile: ./validator/cprof_authorization_handlers.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    do_connect()
    do_authorization_trust_request()
    do_authorization_challenge_request()

    pr.disable()
    pr.print_stats(sort='time')