try:
    from termcolor import colored
except ImportError:
    print 'You should run "pip install termcolor" to fully utilize these utilities.'

    def colored(text, *args, **kwargs):
        return text

class AsciiCell(object):
    def __init__(self, value, color=None, background=None, reverse=False):
        self.value = isinstance(value, str) and value.decode('utf8', 'ignore') or value
        self.color = color
        self.background = background
        self.attrs = reverse and ['reverse'] or []
        self.width = len(value)

class AsciiTable(object):
    def __init__(self, headers):
        self.headers = [ isinstance(x, AsciiCell) and x or AsciiCell(x) for x in headers ]
        self.data = []
        self._widths = [ x.width for x in self.headers ]
        self.left_padding = 1
        self.right_padding = 1

    def add_row(self, data):
        if len(data) != len(self.headers):
            raise Exception('The number of columns in a row must be equal to the header column count.')
        self.data.append([ isinstance(x, AsciiCell) and x or AsciiCell(x) for x in data ])

    def __str__(self):
        self.__unicode__()

    def __unicode__(self):
        self._print()

    def _print_horizontal_rule(self):
        bits = []
        bits.append(u'+')
        for column, width in zip(self.headers, self._widths):
            bits.append(u'-' * (self.right_padding + self.left_padding + width))
            bits.append(u'+')
        print u''.join(bits)

    def _print_headers(self):
        self._print_row(self.headers)

    def _print_data(self):
        for row in self.data:
            self._print_row(row)

    def _print_row(self, row):
        bits = []
        bits.append(u'|')
        for column, cell, width in zip(self.headers, row, self._widths):
            bits.append(colored(u' ' * self.left_padding + cell.value.ljust(width) + u' ' * self.right_padding, cell.color, cell.background, attrs=cell.attrs))
            bits.append(u'|')
        print u''.join(bits)

    def render(self):
        self._calculate_widths()

        self._print_horizontal_rule()
        self._print_headers()
        self._print_horizontal_rule()
        self._print_data()
        self._print_horizontal_rule()

    def _calculate_widths(self):
        for data in self.data:
            for column, cell in enumerate(data):
                self._widths[column] = max(self._widths[column], cell.width)
