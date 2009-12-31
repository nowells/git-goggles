import os
import subprocess

class Repository(object):
    def __init__(self, path=None):
        self.path = os.path.abspath(path or os.path.curdir)

    def git(self, *args, **kwargs):
        split = kwargs.pop('split', False)
        join = kwargs.pop('join', False)

        command = ['git'] + list(args)

        if join:
            p = subprocess.Popen(command)
            p.communicate()
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            output = p.communicate()[0]
            if split:
                output = filter(lambda x: x, output.split('\n'))
            return output

    def fetch(self):
        self.git('fetch')
        self.git('fetch', '--tags')

    def branches(self, remote=None):
        if remote is None:
            return [ x.split()[1].split('/')[2].strip() for x in self.git('show-ref', '--heads', split=True) if not x.endswith('^{}') ]
        else:
            return [ x.split()[1].split('/')[2].strip() for x in self.git('ls-remote', '--heads', remote, split=True) if not x.endswith('^{}') ]

    def tags(self, remote=None):
        if remote is None:
            return [ x.split()[1].split('/')[2].strip() for x in self.git('show-ref', '--tags', split=True) if not x.endswith('^{}') ]
        else:
            return [ x.split()[1].split('/')[2].strip() for x in self.git('ls-remote', '--tags', remote, split=True) if not x.endswith('^{}') ]

    def branch(self):
        return self.git('symbolic-ref', 'HEAD').split('/')[2].strip()
