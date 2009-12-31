import os
import subprocess

class Ref(object):
    def __init__(self, repo, sha, spec):
        self.repo = repo
        self.spec = spec
        self.sha = sha
        self.type, self.name = spec[5:].partition("/")[0::2]

    @property
    def modified(self):
        return self.repo.git('show', '--pretty=format:%ar', self.sha).split('\n')[0].strip()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '<%s %s>' % (self.type, self.name)

    def __repr__(self):
        return self.__unicode__()

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
                output = filter(lambda x: x, map(lambda x: x.strip(), output.split('\n')))
            return output

    @property
    def configs(self):
        return dict([ x.partition('=')[0::2] for x in self.git('config', '--list', split=True) ])

    def fetch(self):
        self.git('fetch')
        self.git('fetch', '--tags')

    def refs(self):
        return [ Ref(self, *x.split()) for x in self.git('show-ref', split=True) ]

    def branches(self, remote=None):
        if remote is None:
            return [ Ref(self, *x.split()) for x in self.git('show-ref', '--heads', split=True) if not x.endswith('^{}') ]
        else:
            return [ Ref(self, *x.split()) for x in self.git('ls-remote', '--heads', remote, split=True) if not x.endswith('^{}') ]

    def tags(self, remote=None):
        if remote is None:
            return [ Ref(self, *x.split()) for x in self.git('show-ref', '--tags', split=True) if not x.endswith('^{}') ]
        else:
            return [ Ref(self, *x.split()) for x in self.git('ls-remote', '--tags', remote, split=True) if not x.endswith('^{}') ]

    def branch(self):
        return self.git('symbolic-ref', 'HEAD').strip().split('/')[2]
