import copy
import subprocess
import sys
import unicodedata

def disable_colored_func(text, *args, **kwargs):
    return text

try:
    from termcolor import colored as colored_func
except ImportError:
    print 'You should run "pip install termcolor" to fully utilize these utilities.'
    colored_func = disable_colored_func

def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    unsupported_platform = (sys.platform in ('win32', 'Pocket PC'))
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if unsupported_platform or not is_a_tty:
        return False
    return True

if not supports_color():
    colored_func = disable_colored_func

class Colored(object):
    disabled = False
    def __call__(self, *args, **kwargs):
        if self.disabled:
            return disable_colored_func(*args, **kwargs)
        return colored_func(*args, **kwargs)

colored = Colored()

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

def terminal_dimensions():
    try:
        # This probably does not work on windows, but it should work just about
        # everywhere else.
        p = subprocess.Popen(['stty', 'size'], stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate(None)
        stdout = force_unicode(stdout)
        stderr = force_unicode(stderr)
        rows, columns = [ int(x) for x in stdout.split() ]
    except:
        rows, columns = 40, 79
    return rows, columns
