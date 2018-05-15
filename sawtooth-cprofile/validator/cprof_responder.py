import cProfile
import unittest

from sawtooth_validator.protobuf import network_pb2
from sawtooth_validator.protobuf import validator_pb2
from sawtooth_validator.protobuf import block_pb2
from sawtooth_validator.protobuf import batch_pb2
from sawtooth_validator.protobuf import transaction_pb2
from sawtooth_validator.journal.responder import Responder
from sawtooth_validator.journal.responder import BlockResponderHandler
from sawtooth_validator.journal.responder import BatchByBatchIdResponderHandler
from sawtooth_validator.journal.responder import \
    BatchByTransactionIdResponderHandler
from sawtooth_validator.journal.responder import ResponderBlockResponseHandler
from sawtooth_validator.journal.responder import ResponderBatchResponseHandler
from test_responder.mock import MockGossip
from test_responder.mock import MockCompleter


class TestResponder():
    def __init__(self):
        self.gossip = MockGossip()
        self.completer = MockCompleter()
        self.responder = Responder(self.completer)
        self.block_request_handler = \
            BlockResponderHandler(self.responder, self.gossip)
        self.block_response_handler = \
            ResponderBlockResponseHandler(self.responder, self.gossip)
        self.batch_request_handler = \
            BatchByBatchIdResponderHandler(self.responder, self.gossip)
        self.batch_response_handler = \
            ResponderBatchResponseHandler(self.responder, self.gossip)
        self.batch_by_txn_request_handler = \
            BatchByTransactionIdResponderHandler(self.responder, self.gossip)


def test_block_responder_handler():
    """
    Test that the BlockResponderHandler correctly broadcasts a received
    request that the Responder cannot respond to, or sends a
    GossipBlockResponse back to the connection_id the handler received
    the request from.
    """
    # The completer does not have the requested block

    testResponder = TestResponder()

    before_message = network_pb2.GossipBlockRequest(
        block_id="ABC",
        nonce="1",
        time_to_live=1)

    after_message = network_pb2.GossipBlockRequest(
        block_id="ABC",
        nonce="1",
        time_to_live=0)

    testResponder.block_request_handler.handle(
        "Connection_1", before_message.SerializeToString())
    # If we cannot respond to the request, broadcast the block request
    # and add to pending request
    # Add the block to the completer and resend the Block Request
    block = block_pb2.Block(header_signature="ABC")
    testResponder.completer.add_block(block)

    message = network_pb2.GossipBlockRequest(
        block_id="ABC",
        nonce="2",
        time_to_live=1)

    testResponder.block_request_handler.handle(
        "Connection_1", message.SerializeToString())


def test_block_responder_handler_requested():
    """
    Test that the BlockResponderHandler correctly broadcasts a received
    request that the Responder cannot respond to, and does not rebroadcast
    the same request.  If we have already recieved the
    request, do nothing.
    """

    testResponder = TestResponder()

    before_message = network_pb2.GossipBlockRequest(
        block_id="ABC",
        nonce="1",
        time_to_live=1)

    after_message = network_pb2.GossipBlockRequest(
        block_id="ABC",
        nonce="1",
        time_to_live=0)

    testResponder.block_request_handler.handle(
        "Connection_1", before_message.SerializeToString())
    # If we cannot respond to the request, broadcast the block request
    # and add to pending request

    testResponder.gossip.clear()

    # Message should be dropped since the same message has already been
    # handled
    testResponder.block_request_handler.handle(
        "Connection_2", before_message.SerializeToString())

    message = network_pb2.GossipBlockRequest(
        block_id="ABC",
        nonce="2",
        time_to_live=1)

    testResponder.block_request_handler.handle(
        "Connection_2", message.SerializeToString())


def test_responder_block_response_handler():
    """
    Test that the ResponderBlockResponseHandler, after receiving a Block
    Response, checks to see if the responder has any pending request for
    that response and forwards the response on to the connection_id that
    had requested it.
    """
    # The Responder does not have any pending requests for block "ABC"
    testResponder = TestResponder()

    block = block_pb2.Block(header_signature="ABC")
    response_message = network_pb2.GossipBlockResponse(
        content=block.SerializeToString())

    testResponder.block_response_handler.handle(
        "Connection_1", (block, response_message.SerializeToString()))

    # ResponderBlockResponseHandler should not send any messages.
    # Handle a request message for block "ABC". This adds it to the pending
    # request queue.
    request_message = \
        network_pb2.GossipBlockRequest(block_id="ABC", time_to_live=1)

    testResponder.block_request_handler.handle(
        "Connection_2", request_message.SerializeToString())

    # Handle the the BlockResponse Message. Since Connection_2 had
    # requested the block but it could not be fulfilled at that time of the
    # request the received BlockResponse is forwarded to Connection_2
    testResponder.block_response_handler.handle(
        "Connection_1", (block, response_message.SerializeToString()))


def test_batch_by_id_responder_handler():
    """
    Test that the BatchByBatchIdResponderHandler correctly broadcasts a
    received request that the Responder cannot respond to, or sends a
    GossipBatchResponse back to the connection_id the handler received
    the request from.
    """
    # The completer does not have the requested batch
    testResponder = TestResponder()

    before_message = network_pb2.GossipBatchByBatchIdRequest(
        id="abc",
        nonce="1",
        time_to_live=1)

    after_message = network_pb2.GossipBatchByBatchIdRequest(
        id="abc",
        nonce="1",
        time_to_live=0)

    testResponder.batch_request_handler.handle(
        "Connection_1", before_message.SerializeToString())
    # Add the batch to the completer and resend the BatchByBatchIdRequest
    message = network_pb2.GossipBatchByBatchIdRequest(
        id="abc",
        nonce="2",
        time_to_live=1)
    batch = batch_pb2.Batch(header_signature="abc")
    testResponder.completer.add_batch(batch)
    testResponder.batch_request_handler.handle(
        "Connection_1", message.SerializeToString())


def test_batch_by_id_responder_handler_requested():
    """
    Test that the BatchByBatchIdResponderHandler correctly broadcasts
    a received request that the Responder cannot respond to, and does not
    rebroadcast the same request again.  If we have already recieved the
    request, do nothing.
    """
    # The completer does not have the requested batch
    testResponder = TestResponder()

    before_message = network_pb2.GossipBatchByBatchIdRequest(
        id="abc",
        nonce="1",
        time_to_live=1)

    after_message = network_pb2.GossipBatchByBatchIdRequest(
        id="abc",
        nonce="1",
        time_to_live=0)
    testResponder.batch_request_handler.handle(
        "Connection_1", before_message.SerializeToString())
    # If we cannot respond to the request broadcast batch request and add
    # to pending request

    testResponder.gossip.clear()

    # Message should be dropped since the same message has already been
    # handled
    testResponder.batch_request_handler.handle(
        "Connection_2", before_message.SerializeToString())

    message = network_pb2.GossipBatchByBatchIdRequest(
        id="abc",
        nonce="2",
        time_to_live=1)

    testResponder.batch_request_handler.handle(
        "Connection_2", message.SerializeToString())


def test_batch_by_transaction_id_response_handler():
    """
    Test that the BatchByTransactionIdResponderHandler correctly broadcasts
    a received request that the Responder cannot respond to, or sends a
    GossipBatchResponse back to the connection_id the handler received
    the request from.
    """
    # The completer does not have the requested batch with the transaction
    testResponder = TestResponder()

    before_message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123"],
        nonce="1",
        time_to_live=1)

    after_message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123"],
        nonce="1",
        time_to_live=0)

    testResponder.batch_by_txn_request_handler.handle(
        "Connection_1", before_message.SerializeToString())

    # If we cannot respond to the request, broadcast batch request and add
    # to pending request
    # BatchByTransactionIdRequest
    message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123"],
        nonce="2",
        time_to_live=1)
    transaction = transaction_pb2.Transaction(header_signature="123")
    batch = batch_pb2.Batch(
        header_signature="abc", transactions=[transaction])
    testResponder.completer.add_batch(batch)
    testResponder.batch_request_handler.handle(
        "Connection_1", message.SerializeToString())


def test_batch_by_transaction_id_response_handler_requested():
    """
    Test that the BatchByTransactionIdResponderHandler correctly broadcasts
    a received request that the Responder cannot respond to, and does not
    rebroadcast the same request again. If we have already recieved the
    request, do nothing.
    """
    # The completer does not have the requested batch with the transaction
    testResponder = TestResponder()

    before_message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123"],
        time_to_live=1)

    after_message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123"],
        time_to_live=0)

    testResponder.batch_by_txn_request_handler.handle(
        "Connection_1", before_message.SerializeToString())

    # If we cannot respond to the request, broadcast batch request and add
    # to pending request

    testResponder.gossip.clear()

    # Message should be dropped since the same message has already been
    # handled
    testResponder.batch_by_txn_request_handler.handle(
        "Connection_2", before_message.SerializeToString())

    message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123"],
        nonce="2",
        time_to_live=1)
    testResponder.batch_by_txn_request_handler.handle(
        "Connection_2", message.SerializeToString())


def test_batch_by_transaction_id_multiple_txn_ids():
    """
    Test that the BatchByTransactionIdResponderHandler correctly broadcasts
    a new request with only the transaction_ids that the Responder cannot
    respond to, and sends a GossipBatchResponse for the transactions_id
    requests that can be satisfied.
    """
    # Add batch that has txn 123
    testResponder = TestResponder()

    transaction = transaction_pb2.Transaction(header_signature="123")
    batch = batch_pb2.Batch(
        header_signature="abc", transactions=[transaction])
    testResponder.completer.add_batch(batch)
    # Request transactions 123 and 456
    message = network_pb2.GossipBatchByTransactionIdRequest(
        ids=["123", "456"],
        time_to_live=1)
    testResponder.batch_by_txn_request_handler.handle(
        "Connection_1", message.SerializeToString())
    testResponder.batch_request_handler.handle(
        "Connection_1", message.SerializeToString())

    # Respond with a BatchResponse for transaction 123

    # Broadcast a BatchByTransactionIdRequest for just 456
    after_message = \
        network_pb2.GossipBatchByTransactionIdRequest(
            ids=["456"],
            time_to_live=0)


def test_responder_batch_response_handler():
    """
    Test that the ResponderBatchResponseHandler, after receiving a Batch
    Response, checks to see if the responder has any pending request for
    that batch and forwards the response on to the connection_id that
    had requested it.
    """
    # The Responder does not have any pending requests for block "ABC"

    testResponder = TestResponder()

    batch = batch_pb2.Batch(header_signature="abc")

    response_message = network_pb2.GossipBatchResponse(
        content=batch.SerializeToString())

    testResponder.batch_response_handler.handle(
        "Connection_1", (batch, response_message.SerializeToString()))

    # request queue.
    request_message = \
        network_pb2.GossipBatchByBatchIdRequest(id="abc", time_to_live=1)

    testResponder.batch_request_handler.handle(
        "Connection_2", request_message.SerializeToString())

    # Handle the the BatchResponse Message. Since Connection_2 had
    # requested the batch but it could not be fulfilled at that time of the
    # request the received BatchResponse is forwarded to Connection_2
    testResponder.batch_response_handler.handle(
        "Connection_1", (batch, response_message.SerializeToString()))


def test_responder_batch_response_txn_handler():
    """
    Test that the ResponderBatchResponseHandler, after receiving a Batch
    Response, checks to see if the responder has any pending request for
    that transactions in the batch and forwards the response on to the
    connection_id that had them.
    """

    testResponder = TestResponder()

    transaction = transaction_pb2.Transaction(header_signature="123")
    batch = batch_pb2.Batch(
        header_signature="abc", transactions=[transaction])

    response_message = network_pb2.GossipBatchResponse(
        content=batch.SerializeToString())

    request_message = \
        network_pb2.GossipBatchByTransactionIdRequest(
            ids=["123"],
            time_to_live=1)

    # Send BatchByTransaciontIdRequest for txn "123" and add it to the
    # pending request cache
    testResponder.batch_request_handler.handle(
        "Connection_2", request_message.SerializeToString())

    # Send Batch Response that contains the batch that has txn "123"
    testResponder.batch_response_handler.handle(
        "Connection_1", (batch, response_message.SerializeToString()))


if __name__ == '__main__':
    print("\n====== cProfile: responder.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    test_block_responder_handler()
    test_block_responder_handler_requested()
    test_responder_block_response_handler()
    test_batch_by_id_responder_handler()
    test_batch_by_id_responder_handler_requested()
    test_batch_by_transaction_id_response_handler()
    test_batch_by_transaction_id_response_handler_requested()
    test_batch_by_transaction_id_multiple_txn_ids()
    test_responder_batch_response_handler()
    test_responder_batch_response_txn_handler()

    pr.disable()
    pr.print_stats(sort='time')
