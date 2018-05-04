from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory



context = create_context('secp256k1')
signer = CryptoFactory(context).new_signer(context.new_random_private_key())

def getKey():
  return signer.get_public_key().as_hex()

if __name__ == '__main__':
  from timeit import Timer
  t = Timer("getKey()", "from __main__ import getKey")
  print("%.2f ms/1000 ops" % (1000000 * t.timeit(number=100000)/100000))
  