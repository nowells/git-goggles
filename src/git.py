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

    def __branches(self):
        branches = self.git('branch', '-a', split=True)
        for branch in branches:
            _, current, branch = branch.rpartition('*')
            current, branch = bool(current), branch.strip()
            remote, _, branch = branch.rpartition('/')
            _, _, remote = remote.rpartition('remotes/')
            remote = remote or None
            yield current, remote, branch

    def tags(self):
        return self.git('tag', split=True)

    def branch(self):
        for current, remote, branch in self.__branches():
            if current:
                return branch
        return None

    def branches(self, remote=None):
        return [ branch for current, _remote, branch in self.__branches() if remote == _remote ]
