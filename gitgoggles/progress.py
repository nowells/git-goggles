import logging
from logging import StreamHandler
import StringIO
import sys

class ProgressStreamHandler(StreamHandler):
    def __init__(self, *args, **kwargs):
        self.stdout = sys.stdout
        self.capture_stdout = StringIO.StringIO()
        self.spinner = '-/|\\'
        self.msg = ''
        StreamHandler.__init__(self, *args, **kwargs)

    def swap_stdout(self):
        self.stdout = sys.stdout
        sys.__stdout__.write('\033[s')
        sys.stdout = handler.capture_stdout

    def emit(self, record):
        self.msg = record.msg
        self.display_message()

    def display_message(self):
        msg = ' %s   %s' % (self.spinner[0], self.msg)
        self.spinner = self.spinner[1:] + self.spinner[:1]
        self.clear_line()
        sys.__stdout__.write(msg)

    def clear_line(self):
        sys.__stdout__.write('\033[u')
        sys.__stdout__.write('\033[s')
        sys.__stdout__.write('\033[K')

handler = ProgressStreamHandler()
log = logging.getLogger('progress')
log.setLevel(logging.INFO)

def enable_progress():
    handler.swap_stdout()
    log.addHandler(handler)

def disable_progress():
    sys.stdout = handler.stdout
    sys.stdout.write('\033[u')
    sys.stdout.write('\033[K')
    handler.capture_stdout.seek(0)
    print handler.capture_stdout.read()
