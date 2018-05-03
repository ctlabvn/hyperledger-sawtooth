import cProfile
from sawtooth_ias_client.ias_client import IasClient
from tests.unit import mock_ias_server

URL = "http://127.0.0.1:8008"
mockServer = mock_ias_server.create(URL)
mockServer.start("up")
client = IasClient(URL, None, 5)


def test_get_signature_revocation_lists(benchmark):
    result = benchmark(client.get_signature_revocation_lists, gid="gid")
    return


def test_post_verify_attestation(benchmark):
    result = benchmark(client.post_verify_attestation,
                       "thisisaquote", "thisisamanifest", 34608138615)
    return
