import unittest
from sawtooth_poet_common import sgx_structs

class TestStringMethods(unittest.TestCase):

    def test_split(self):
        s = 'hello world'
        sgx_cpu_svn = sgx_structs.SgxCpuSvn()

        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


        with self.assertRaises(ValueError):
            sgx_cpu_svn.parse_from_bytes(
                b'\x00' * (sgx_structs.SgxCpuSvn.STRUCT_SIZE - 1))

if __name__ == '__main__':
    unittest.main()