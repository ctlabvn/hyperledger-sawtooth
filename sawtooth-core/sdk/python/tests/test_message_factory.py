from sawtooth_processor_test.message_factory import _signer
from sawtooth_processor_test.message_factory import MessageFactory

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import create_context

from sawtooth_sdk.protobuf.processor_pb2 import TpProcessResponse

from sawtooth_poet_common.protobuf.validator_registry_pb2 import ValidatorMap

import hashlib

from uuid import uuid4

import cbor

def test__signer(benchmark):
	result = benchmark(_signer)
	return

def test_init_battleship_message(benchmark):
	result = benchmark(MessageFactory, "battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	return

def test_init_settings_message(benchmark):
	result = benchmark(MessageFactory, "sawtooth_settings", "1.0", "000000", None)
	return

def test_init_identity_message(benchmark):
	result = benchmark(MessageFactory, "sawtooth_identity", "1.0", "00001d", None)
	return

def test_init_intkey_message(benchmark):
	result = benchmark(MessageFactory, "intkey", "1.0", hashlib.sha512('intkey'.encode('utf-8')).hexdigest()[0:6], None)
	return

def test_init_xo_message(benchmark):
	result = benchmark(MessageFactory, "xo", "1.0", MessageFactory.sha512("xo".encode("utf-8"))[0:6], None)
	return

def test_init_validtor_registry(benchmark):
	PRIVATE = '2f1e7b7a130d7ba9da0068b3bb0ba1d79e7e77110302c9f746c3c2a63fe40088'
	context = create_context('secp256k1')
	private_key = Secp256k1PrivateKey.from_hex(PRIVATE)
	signer = CryptoFactory(context).new_signer(private_key)
	result = benchmark(MessageFactory, "sawtooth_validator_registry", "1.0", "6a4372", signer)
	return

# def test_namespace(benchmark):
# 	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
# 	result = benchmark(MessageFactory.namespace, battleshipMessage)

def test_sha512(benchmark):
	name = uuid4().hex[:20]
	result = benchmark(MessageFactory.sha512, cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000}))
	return

def test_sha256(benchmark):
	name = uuid4().hex[:20]
	result = benchmark(MessageFactory.sha256, cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000}))
	return

def test_get_public_key(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	result = benchmark(MessageFactory.get_public_key, battleshipMessage)
	return

def test_create_tp_register(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	result = benchmark(MessageFactory.create_tp_register, battleshipMessage)
	return

def test_create_tp_response(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	result = benchmark(MessageFactory.create_tp_response, battleshipMessage, "OK")
	return

def test__create_transaction_header(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	name = uuid4().hex[:20]
	result = benchmark(MessageFactory._create_transaction_header, 
		battleshipMessage, cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000}), 
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:],
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:], [])
	return

def test__create_signature(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	name = uuid4().hex[:20]
	payload = cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000})
	inputs = battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:]
	outputs = battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:]
	deps = []
	header = battleshipMessage._create_transaction_header(payload, inputs, outputs, deps)
	# result = benchmark(MessageFactory._create_signature, battleshipMessage, header)
	return

def test__create_header_and_sig(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	name = uuid4().hex[:20]
	result = benchmark(MessageFactory._create_header_and_sig, battleshipMessage,
		cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000}),
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:],
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:], [])
	return

def test_create_transaction(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	name = uuid4().hex[:20]
	benchmark(MessageFactory.create_transaction, 
		battleshipMessage,
		cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000}),
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:],
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:], [])
	return

def test__validate_addresses(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	benchmark(MessageFactory._validate_addresses, [address])
	return

def test_create_tp_process_request(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	name = uuid4().hex[:20]
	benchmark(MessageFactory.create_tp_process_request,
		battleshipMessage,
		cbor.dumps({'Name': name, 'Verb': 'set', 'Value': 1000}),
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:],
		battleshipMessage.namespaces[0] + MessageFactory.sha512(name.encode())[-64:], [])
	return


# def test_create_batch(benchmark):
# 	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)

def test_create_get_request(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	benchmark(MessageFactory.create_get_request, battleshipMessage, [address])	
	return

def test_create_get_response(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()	
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	data = ValidatorMap().SerializeToString()
	benchmark(MessageFactory.create_get_response, battleshipMessage, {address: data})
	return

def test_create_set_request(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()	
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	data = ValidatorMap().SerializeToString()
	benchmark(MessageFactory.create_set_request, battleshipMessage, {address: data})
	return	

def test_create_set_response(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	benchmark(MessageFactory.create_set_response, battleshipMessage, [address])	
	return

def test_create_delete_request(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	benchmark(MessageFactory.create_delete_request, battleshipMessage, [address])	
	return

def test_create_delete_response(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	context = create_context("secp256k1")
	publicKey = battleshipMessage.get_public_key()
	address = battleshipMessage.namespaces[0] + MessageFactory.sha256(publicKey.encode("utf-8"))
	benchmark(MessageFactory.create_delete_response, battleshipMessage, [address])	
	return

def test_create_add_event_request(benchmark):
	key = "policy1"
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	benchmark(MessageFactory.create_add_event_request, battleshipMessage, "settings/update", [("update", key)])
	return

def test_create_add_event_response(benchmark):
	battleshipMessage = MessageFactory("battleship", "1.0", MessageFactory.sha512("battleship".encode("utf-8"))[0:6], None)
	benchmark(MessageFactory.create_add_event_response, battleshipMessage)
	return