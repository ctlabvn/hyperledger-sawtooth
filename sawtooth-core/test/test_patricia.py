from unittest import main, TestCase
from patricia.merkle_trie import MerkleTrie, _NonTerminal

__author__ = 'tupt'
__version__ = 9


class MerkleTrieTests(TestCase):
    # def testInitContains(self):
    #     T = MerkleTrie(key='value')
    #     T = MerkleTrie(**T)
    #     self.assertTrue('key' in T)
    #     self.assertFalse('keys' in T)
    #     self.assertFalse('ke' in T)
    #     self.assertFalse('kex' in T)

    # def testSetGetDel(self):
    #     T = MerkleTrie()
    #     T['foo'] = 1
    #     T['bar'] = 2
    #     T['baz'] = 3
    #     self.assertTrue('foo' in T)
    #     self.assertTrue('bar' in T)
    #     self.assertTrue('baz' in T)
    #     self.assertEqual(T['foo'], 1)
    #     self.assertEqual(T['bar'], 2)
    #     self.assertEqual(T['baz'], 3)
    #     self.assertRaises(KeyError, T.__getitem__, 'ba')
    #     self.assertRaises(KeyError, T.__getitem__, 'fool')
    #     del T['bar']
    #     self.assertRaises(KeyError, T.__getitem__, 'bar')
    #     self.assertEqual(T['baz'], 3)

    # def testEmptyStringKey(self):
    #     T = MerkleTrie(2, foo=1)
    #     self.assertTrue('foo' in T)
    #     self.assertTrue('' in T)
    #     del T['']
    #     self.assertRaises(KeyError, T.__getitem__, '')

    # def testIterator(self):
    #     T = MerkleTrie(ba=2, baz=3, fool=1)
    #     self.assertListEqual(sorted(['fool', 'ba', 'baz']), sorted(list(T)))
    #     T[''] = 0
    #     self.assertEqual(sorted(['', 'fool', 'ba', 'baz']), sorted(list(T)))

    # def testSingleEntry(self):
    #     T = MerkleTrie(foo=5)
    #     self.assertListEqual(['foo'], list(T.keys()))
    #     self.assertListEqual([5], list(T.values()))
    #     self.assertListEqual([('foo', 5)], list(T.items()))

    # def testValues(self):
    #     T = MerkleTrie()
    #     T['ba'] = 2
    #     T['baz'] = "hey's"
    #     T['fool'] = 1.5
    #     self.assertListEqual(sorted(["2", "hey's", "1.5"]), sorted([str(v) for v in T.values()]))

    # def testStrRepr(self):
    #     T = MerkleTrie()
    #     T['ba'] = 2
    #     T['baz'] = "hey's"
    #     T['fool'] = 1.5
    #     result = repr(T)
    #     print(result)
    #     self.assertTrue(result.startswith("MerkleTrie({"), result)
    #     self.assertTrue(result.endswith('})'), result)
    #     self.assertTrue("'ba': 2" in result, result)
    #     self.assertTrue("'baz': \"hey's\"" in result, result)
    #     self.assertTrue("'fool': 1.5" in result, result)

    # def testGetItems(self):
    #     T = MerkleTrie()
    #     T['ba'] = 2
    #     T['baz'] = 3
    #     T['fool'] = 1
    #     self.assertEqual(('ba', 2), T.item('bar'))
    #     self.assertEqual(1, T.value('fool'))
    #     self.assertRaises(KeyError, T.key, 'foo')
    #     T[''] = 0
    #     self.assertEqual(('', 0), T.item(''))
    #     self.assertEqual('', T.key('foo'))

    # def testGetExactMatch(self):
    #     T = MerkleTrie(exact=5)
    #     self.assertListEqual(['exact'], list(T.keys('exact')))
    #     self.assertListEqual([5], list(T.values('exact')))
    #     self.assertListEqual([('exact', 5)], list(T.items('exact')))

    # def testFakeDefault(self):
    #     T = MerkleTrie()
    #     fake = _NonTerminal()
    #     self.assertEqual(fake, T.value('foo', default=fake))

    # def testLongRootValue(self):
    #     T = MerkleTrie(1, 2)
    #     self.assertEqual((1, 2), T[''])

    # def testIterItems(self):
    #     T = MerkleTrie(ba=2, baz=3, fool=1)
    #     self.assertListEqual(['ba', 'baz'], list(T.keys('bazar')))
    #     self.assertListEqual([('fool', 1)], list(T.items('fools')))
    #     self.assertListEqual([], list(T.values('others')))

    # def testIsPrefix(self):
    #     T = MerkleTrie(bar=2, baz=3, fool=1)
    #     self.assertTrue(T.isPrefix('ba'))
    #     self.assertFalse(T.isPrefix('fools'))
    #     self.assertTrue(T.isPrefix(''))

    # def testIterPrefix(self):
    #     T = MerkleTrie()
    #     T['b'] = 1
    #     T['baar'] = 2
    #     T['baahus'] = 3
    #     self.assertListEqual(sorted(['baar', 'baahus']), sorted(list(T.iter('ba'))))
    #     self.assertListEqual(sorted(['baar', 'baahus']), sorted(list(T.iter('baa'))))
    #     self.assertListEqual(sorted(['b', 'baar', 'baahus']), sorted(list(T.iter('b'))))
    #     self.assertListEqual(sorted([]), sorted(list(T.iter('others'))))

    # def testOffsetMatching(self):
    #     T = MerkleTrie()
    #     T['foo'] = 1
    #     T['baar'] = 2
    #     T['baarhus'] = 3
    #     T['bazar'] = 4
    #     txt = 'The fool baal baarhus in the bazar!'
    #     keys = []
    #     values = []
    #     items = []
    #     for i in range(len(txt)):
    #         values.extend(T.values(txt, i))
    #     for i in range(len(txt)):
    #         keys.extend(T.keys(txt, i))
    #     for i in range(len(txt)):
    #         items.extend(T.items(txt, i))
    #     self.assertListEqual([1, 2, 3, 4], values)
    #     self.assertListEqual(['foo', 'baar', 'baarhus', 'bazar'], keys)
    #     self.assertListEqual([('foo', 1), ('baar', 2), ('baarhus', 3), ('bazar', 4)], items)

    # def testKeyPresenceOnly(self):
    #     T = MerkleTrie(foo=True, baar=True, baarhus=True, bazar=True)
    #     txt = 'The fool baal baarhus in the bazar!'
    #     presence = [4, 14, 29]
    #     for i in range(len(txt)):
    #         if T.value(txt, i, default=False):
    #             self.assertTrue(i in presence,
    #                             '{} {} "{}"'.format(str(presence), i, txt[i:]))
    #             presence.remove(i)
    #     self.assertEqual(0, len(presence), str(presence))

    # def testWindowMatching(self):
    #     T = MerkleTrie(foo=1, foobar=2)
    #     self.assertListEqual(['foo'], list(T.keys("foobar", 0, 3)))
    #     self.assertListEqual([1], list(T.values("a foobar!", 2, 7)))
    #     self.assertListEqual([('foo', 1), ('foobar', 2)],
    #                          list(T.items("a foobar!", 2, 8)))
    #     self.assertEqual('foo', T.key("foobar", 0, 3))
    #     self.assertEqual(1, T.value("a foobar!", 2, 7))
    #     self.assertEqual(('foobar', 2), T.item("a foobar!", 2, 8))

    # def testBorderlineValues(self):
    #     T = MerkleTrie(foo=1, bar=2)
    #     self.assertEqual('foo', T.key('foo', -3))
    #     self.assertEqual('foo', T.key('foo', -4))
    #     self.assertEqual('foo', T.key('foo', -4, 3))
    #     self.assertEqual(None, T.key('foo', -3, -4, None))
    #     self.assertEqual(None, T.key('foo', -4, -4, None))

    def testFullTree(self):
        T = MerkleTrie(zero=0, one=1, two=2, three=3, four=4, five=5, six=6, seven=7,
             eight=8, nine=9, ten=10, eleven=11, twelve=12, thirteen=13,
             fourteen=10, fifteen=15, sixteen=16, seventeen=17, eighteen=18,
             nineteen=19, twenty=20, thirty=30, fourty=40, fifty=50, sixty=60,
             seventy=70, eighty=80, ninety=90, hundred=100)

        items = T.items("twenty")
        print(list(items))

if __name__ == '__main__':
    main()