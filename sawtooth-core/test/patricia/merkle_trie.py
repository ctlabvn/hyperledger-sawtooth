"""
Patricia merkle trie for sawtooth implementation
"""
class _NonTerminal():
  pass


__NON_TERMINAL__ = _NonTerminal()


# recursion functions


def _count(node):
    "Count the number of terminal nodes in this branch."
    count = 0 if (node._value is __NON_TERMINAL__) else 1
    for _, child in node._edges.values():
        count += _count(child)
    return count

def _keys(node, accu):
    "Yield keys of terminal nodes in this branch."
    for key, value in _items(node, accu):
        yield key

def _items(node, accu):
    "Yield key, value pairs of terminal nodes in this branch."
    if node._value is not __NON_TERMINAL__:
        yield ''.join(accu), node._value
    for edge, child in node._edges.values():
        accu.append(edge)
        yield from _items(child, accu)            
        accu.pop()        

def _values(node):
    "Yield values of terminal nodes in this branch."
    if node._value is not __NON_TERMINAL__:
        yield node._value
    for edge, child in node._edges.values():
        yield from _values(child)


class MerkleTrie():

    def __init__(self, *value, **branch):
        """
        Create a new tree node.
        Any arguments will be used as the ``value`` of this node.
        If keyword arguments are given, they initialize a whole ``branch``.
        Note that `None` is a valid value for a node.
        """
        self._edges = {}
        self._value = __NON_TERMINAL__
        if len(value):
            if len(value) == 1:
                self._value = value[0]
            else:
                self._value = value
        for key, val in branch.items():
            self[key] = val


    @staticmethod
    def __offsets(strlen, start, end):
        # Return the correct start, end offsets for a string of length `strlen`.
        return (max(0, strlen + start) if start < 0 else start,
                strlen if end is None else end)    



    @staticmethod
    def __check(value, match, default):
        if value is not __NON_TERMINAL__:
            return match, value
        elif default is not __NON_TERMINAL__:
            return None, default
        else:
            raise KeyError(match)


    def _find(self, path, start, *end):        
        if start < len(path) and path[start] in self._edges:
            edge, child = self._edges[path[start]]            
            if path.startswith(edge, start, *end):
                return child, start + len(edge)
        return None, start  # return None



    def _next(self, path, start, *end):
        try:
            edge, child = self._edges[path[start]]
            if path.startswith(edge, start, *end):
                return child, start + len(edge)
        except KeyError:
            pass
        raise KeyError(path)  # raise error


    def _scan(self, rvalFun, string, start=0, *end):
        node = self
        start, _ = MerkleTrie.__offsets(len(string), start, None)
        while node is not None:
            print(node)
            if node._value is not __NON_TERMINAL__:
                yield rvalFun(string, start, node._value)
            node, start = node._find(string, start, *end)


    def __setitem__(self, key, value):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            if key[idx] in node._edges:
                node, idx = node.__followEdge(key, idx)
            else:
                # no common prefix, create a new edge and (leaf) node
                node._edges[key[idx]] = (key[idx:], MerkleTrie(value))
                break
        else:
            node._value = value


    def __followEdge(self, key, idx):
        edge, child = self._edges[key[idx]]
        if key.startswith(edge, idx):
            # the whole prefix matches; advance
            return child, idx + len(edge)
        else:
            # split edge after the matching part of the key
            pos = 1
            last = min(len(edge), len(key) - idx)
            while pos < last and edge[pos] == key[idx + pos]:
                pos += 1
            split = MerkleTrie()
            split._edges[edge[pos]] = (edge[pos:], child)
            self._edges[key[idx]] = (edge[:pos], split)
            return split, idx + pos


    def __getitem__(self, key):
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            node, idx = node._next(key, idx)
        if node._value is __NON_TERMINAL__:
            raise KeyError(key)
        else:
            return node._value


    def __delitem__(self, key):        
        node = self
        keylen = len(key)
        idx = 0
        while keylen != idx:
            node, idx = node._next(key, idx)
        if node._value is __NON_TERMINAL__:
            raise KeyError(key)
        node._value = __NON_TERMINAL__


    def __contains__(self, key):
        node = self
        keylen = len(key)
        idx = 0
        while idx != keylen and node is not None:
            node, idx = node._find(key, idx)
        return False if node is None else (node._value is not __NON_TERMINAL__)


    def __iter__(self):
        return _keys(self, [])

    def __len__(self):
        return _count(self)

    def __repr__(self):
        string = ['MerkleTrie({']
        first = True
        for key, value in _items(self, []):
            if first:
                first = False
            else:
                string.append(', ')
            string.append(repr(key))
            string.append(': ')
            string.append(repr(value))
        string.append('})')
        return ''.join(string)

    def key(self, string, start=0, end=None, default=__NON_TERMINAL__):
        """
        Return the longest key that is a prefix of ``string`` (beginning at
        ``start`` and ending at ``end``).
        If no key matches, raise a `KeyError` or return the ``default`` value
        if it was set.
        """
        return self.item(string, start, end, default)[0]

    def keys(self, *scan):
        """
        Return all keys (that are a prefix of ``string``
        (beginning at ``start`` (and terminating before ``end``))).
        """
        l = len(scan)
        if l == 0:
            return _keys(self, [])
        else:
            if l == 1:
                scan = (scan[0], 0)
            getKey = lambda string, idx, value: string[scan[1]:idx]
            return self._scan(getKey, *scan)


    def value(self, string, start=0, end=None, default=__NON_TERMINAL__):
        """
        Return the value of the longest key that is a prefix of ``string``
        (beginning at ``start`` and ending at ``end``).
        If no key matches, raise a `KeyError` or return the ``default`` value
        if it was set.
        """
        return self.item(string, start, end, default)[1]


    def values(self, *scan):
        """
        Return all values (for keys that are a prefix of ``string``
        (beginning at ``start`` (and terminating before ``end``))).
        """
        l = len(scan)
        if l == 0:
            return _values(self)
        else:
            if l == 1:
                scan = (scan[0], 0)
            getValue = lambda string, idx, value: value
            return self._scan(getValue, *scan)


    def item(self, string, start=0, end=None, default=__NON_TERMINAL__):
        """
        Return the key, value pair of the longest key that is a prefix of
        ``string`` (beginning at ``start`` and ending at ``end``).
        If no key matches, raise a `KeyError` or return the `None`,
        ``default`` pair if any ``default`` value was set.
        """
        node = self
        strlen = len(string)
        start, end = MerkleTrie.__offsets(strlen, start, end)
        idx = start
        last = self._value
        while idx < strlen:
            node, idx = node._find(string, idx, end)
            if node is None:
                break
            elif node._value is not __NON_TERMINAL__:
                last = node._value
        return MerkleTrie.__check(last, string[start:idx], default)


    def items(self, *scan):
        """
        Return all key, value pairs (for keys that are a prefix of ``string``
        (beginning at ``start`` (and terminating before ``end``))).
        """
        l = len(scan)
        if l == 0:
            return _items(self, [])
        else:
            if l == 1:
                scan = (scan[0], 0)
            getItem = lambda string, idx, value: (string[scan[1]:idx], value)
            return self._scan(getItem, *scan)


    def isPrefix(self, prefix):
        "Return True if any key starts with ``prefix``."
        node = self
        plen = len(prefix)
        idx = 0
        while idx < plen:
            len_left = plen - idx
            for edge, child in node._edges.values():
                e = edge[:len_left] if (len_left < len(edge)) else edge
                if prefix.startswith(e, idx):
                    node = child
                    idx += len(edge)
                    break
            else:
                return False
        return True


    def iter(self, prefix):
        "Return an iterator over all keys that start with ``prefix``."
        node = self
        plen = len(prefix)
        idx = 0
        while idx < plen:
            try:
                node, idx = node._next(prefix, idx)
            except KeyError:
                break
        return node._accumulate(prefix, idx)


    def _accumulate(self, prefix, idx):
        node = self
        accu = [prefix]
        if idx != len(prefix):
            remainder = prefix[idx:]
            for edge, child in node._edges.values():
                if edge.startswith(remainder):
                    node = child
                    accu.append(edge[len(remainder):])
                    break
            else:
                return iter([])
        return _keys(node, accu)




