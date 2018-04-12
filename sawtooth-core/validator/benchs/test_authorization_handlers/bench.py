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
# ------------------------------------------------------------------------------

# pylint: disable=invalid-name

import os

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from sawtooth_validator.networking.interconnect import AuthorizationType
from sawtooth_validator.networking.interconnect import ConnectionStatus
from sawtooth_validator.networking.dispatch import HandlerStatus

from sawtooth_validator.networking.handlers import ConnectHandler
from sawtooth_validator.networking.handlers import \
    AuthorizationTrustRequestHandler
from sawtooth_validator.networking.handlers import \
    AuthorizationChallengeRequestHandler
from sawtooth_validator.networking.handlers import \
    AuthorizationChallengeSubmitHandler
from sawtooth_validator.networking.handlers import \
    PingHandler

from sawtooth_validator.protobuf.authorization_pb2 import ConnectionRequest
from sawtooth_validator.protobuf.authorization_pb2 import RoleType
from sawtooth_validator.protobuf.authorization_pb2 import \
    AuthorizationTrustRequest
from sawtooth_validator.protobuf.authorization_pb2 import \
    AuthorizationChallengeRequest
from sawtooth_validator.protobuf.authorization_pb2 import \
    AuthorizationChallengeSubmit
from sawtooth_validator.protobuf import validator_pb2
from sawtooth_validator.protobuf.network_pb2 import PingRequest

from test_authorization_handlers.mock import MockNetwork
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

def test_connect(benchmark):
    """
    Test the ConnectHandler correctly responds to a ConnectionRequest.
    """
    handler_status = benchmark(do_connect)
    assert handler_status.status == HandlerStatus.RETURN
    assert handler_status.message_type == \
        validator_pb2.Message.AUTHORIZATION_CONNECTION_RESPONSE



def do_ping_handler():
    """
    Test the PingHandler returns a NetworkAck if the connection has
    has finished authorization.
    """
    ping = PingRequest()
    network = MockNetwork(
        {},
        connection_status={
            "connection_id": ConnectionStatus.CONNECTED
        })
    handler = PingHandler(network)
    handler_status = handler.handle("connection_id",
                                    ping.SerializeToString())
    return handler_status

def test_ping_handler(benchmark):    
    handler_status = benchmark(do_ping_handler)
    assert handler_status.status == HandlerStatus.RETURN
    assert handler_status.message_type == validator_pb2.Message.PING_RESPONSE


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

def test_authorization_trust_request(benchmark):
    handler_status = benchmark(do_authorization_trust_request)
    assert handler_status.status ==  HandlerStatus.RETURN
    assert handler_status.message_type == validator_pb2.Message.AUTHORIZATION_TRUST_RESPONSE


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

def test_authorization_challenge_request(benchmark):    
    handler_status = benchmark(do_authorization_challenge_request)
    assert handler_status.status ==  HandlerStatus.RETURN
    assert handler_status.message_type == validator_pb2.Message.AUTHORIZATION_CHALLENGE_RESPONSE



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

def test_authorization_challenge_submit(benchmark):
    handler_status = benchmark(do_authorization_challenge_submit)
    assert handler_status.status ==  HandlerStatus.RETURN
    assert handler_status.message_type == validator_pb2.Message.AUTHORIZATION_CHALLENGE_RESULT


