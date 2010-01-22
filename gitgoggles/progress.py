import atexit
import logging
import StringIO
import sys
from gitgoggles.utils import console, force_unicode, force_str

class ProgressStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        self._stdout = sys.stdout
        self._capture_stdout = StringIO.StringIO()
        self.spinner = '-\\|/'
        self.msg = ''
        self.max_length = 0
        logging.StreamHandler.__init__(self, *args, **kwargs)

    def capture_stdout(self):
        self._stdout = sys.stdout
        sys.stdout = self._capture_stdout

    def uncapture_stdout(self):
        sys.__stdout__.write(''.ljust(self.max_length))
        sys.__stdout__.write('\r')
        sys.stdout = self._stdout
        console(force_unicode(self._capture_stdout.getvalue()))

    def emit(self, record):
        if self.msg != record.msg:
            self.msg = record.msg
            msg = ' %s   %s' % (self.spinner[0], self.msg)
            self.max_length = max(len(msg), self.max_length)
            self.spinner = self.spinner[1:] + self.spinner[:1]
            sys.__stdout__.write(force_str(msg.ljust(self.max_length)))
            sys.__stdout__.write('\r')

def enable_progress():
    handler = ProgressStreamHandler()
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    handler.capture_stdout()
    atexit.register(handler.uncapture_stdout)

log = logging.getLogger('progress')
