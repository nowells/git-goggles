import copy
import sys
import unicodedata

def force_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        # Normalize the unicode data to have characters that in NFKD format would be represented by 2 characters, instead of 1.
        obj = unicodedata.normalize('NFKC', obj)
    return obj

def force_str(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, str):
            obj = obj.encode(encoding)
    return obj

def console(obj):
    sys.stdout.write(force_str(obj))

class AccumulatorDict(dict):
    def __init__(self, default, *args, **kwargs):
        self.__default = default

    def __getitem__(self, key):
        if key not in self:
            self[key] = copy.copy(self.__default)
        return super(AccumulatorDict, self).__getitem__(key)

def memoize(func):
    def _(self, *args, **kwargs):
        if not hasattr(self, '__memoize_cache'):
            self.__memoize_cache = AccumulatorDict(AccumulatorDict({}))
        key = tuple([ tuple(args), tuple([ tuple([x, y]) for x, y in kwargs.items() ]) ])
        if key not in self.__memoize_cache[func]:
            self.__memoize_cache[func][key] = func(self, *args, **kwargs)
        return self.__memoize_cache[func][key]
    return _