import logging
from logging import StreamHandler
import StringIO
import sys

class ProgressStreamHandler(StreamHandler):
    def __init__(self, *args, **kwargs):
        sys.__stdout__.write('\033[s')
        StreamHandler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.__clear_line()
        sys.__stdout__.write(record.msg)

    def __clear_line(self):
        sys.__stdout__.write('\033[u')
        sys.__stdout__.write('\033[s')
        sys.__stdout__.write('\033[K')

log = logging.getLogger('progress')
log.setLevel(logging.INFO)

def enable_progress():
    stdout = StringIO.StringIO()
    sys.stdout = stdout
    log.addHandler(ProgressStreamHandler())

def disable_progress():
    stdout = sys.stdout
    stdout.seek(0)
    sys.__stdout__.write('\033[u')
    sys.__stdout__.write('\033[K')
    sys.stdout = sys.__stdout__
    print stdout.read()
