import cProfile
from sawtooth_ias_client.ias_client import IasClient
import mock_ias_server


URL = "http://127.0.0.1:8008"
mockServer = mock_ias_server.create(URL)
mockServer.start("up")
client = IasClient(URL, None, 5)

def do_post_verify_attestation():
    client.post_verify_attestation(
                        quote="thisisaquote",
                        manifest="thisisamanifest",
                        nonce=34608138615)

def do_get_signature_revocation_lists():
    client.get_signature_revocation_lists(gid="gid")

if __name__ == '__main__':
    print("\n====== cProfile: ./utility/ias_client/cprof_ias_client.py ======\n")
    pr = cProfile.Profile()
    pr.enable()
    do_post_verify_attestation()
    do_get_signature_revocation_lists()

    pr.disable()
    pr.print_stats(sort='time')