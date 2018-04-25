import cProfile
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing.secp256k1 import Secp256k1PublicKey


KEY1_PRIV_HEX = \
    "2f1e7b7a130d7ba9da0068b3bb0ba1d79e7e77110302c9f746c3c2a63fe40088"
KEY1_PUB_HEX = \
    "026a2c795a9776f75464aa3bda3534c3154a6e91b357b1181d3f515110f84b67c5"

KEY2_PRIV_HEX = \
    "51b845c2cdde22fe646148f0b51eaf5feec8c82ee921d5e0cbe7619f3bb9c62d"
KEY2_PUB_HEX = \
    "039c20a66b4ec7995391dbec1d8bb0e2c6e6fd63cd259ed5b877cb4ea98858cf6d"

MSG1 = "test"
MSG1_KEY1_SIG = ("5195115d9be2547b720ee74c23dd841842875db6eae1f5da8605b050a49e"
                 "702b4aa83be72ab7e3cb20f17c657011b49f4c8632be2745ba4de79e6aa0"
                 "5da57b35")

MSG2 = "test2"
MSG2_KEY2_SIG = ("d589c7b1fa5f8a4c5a389de80ae9582c2f7f2a5e21bab5450b670214e5b1"
                 "c1235e9eb8102fd0ca690a8b42e2c406a682bd57f6daf6e142e5fa4b2c26"
                 "ef40a490")

def do_test_hex_key():
    Secp256k1PrivateKey.from_hex(hex_str=KEY1_PRIV_HEX)
    

def do_test_single_key_signing():
    context = create_context("secp256k1")
    factory = CryptoFactory(context)
    priv_key = Secp256k1PrivateKey.from_hex(KEY1_PRIV_HEX)    
    signer = factory.new_signer(priv_key)
    signer.sign(MSG1.encode())


def do_test_verification():
    context = create_context("secp256k1")
    factory = CryptoFactory(context)
    pub_key1 = Secp256k1PublicKey.from_hex(KEY1_PUB_HEX)
    context.verify(signature=MSG1_KEY1_SIG, message= MSG1.encode(), public_key = pub_key1)

if __name__ == '__main__':
    print("\n====== cProfile: ./signing/cprof_secp256k1_signer.py ======\n")
    pr = cProfile.Profile()
    pr.enable()

    do_test_hex_key()
    do_test_single_key_signing()
    do_test_verification()

    pr.disable()
    pr.print_stats(sort='time')