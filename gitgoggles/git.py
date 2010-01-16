import copy
import os
import subprocess

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

class Ref(object):
    def __new__(cls, repo, sha, refspec):
        if cls != Ref:
            return object.__new__(cls)

        ref_type, name = refspec[5:].partition("/")[0::2]
        if ref_type in ('heads', 'remotes',):
            return Branch(repo, sha, refspec)
        elif ref_type in ('tags',):
            return Tag(repo, sha, refspec)
        return object.__new__(cls)

    def __init__(self, repo, sha, refspec):
        self.repo = repo
        self.refspec = refspec
        self.sha = sha

        self.ref_type, self.name = refspec[5:].partition("/")[0::2]
        self.shortname = '/' in self.name and self.name.partition("/")[2] or self.name

    @property
    @memoize
    def modified(self):
        return self.repo.git('show', '--pretty=format:%ar', self.sha).split('\n')[0].strip()

    def __unicode__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

class Branch(Ref):
    def __new__(cls, repo, sha, refspec):
        if cls != Branch:
            return object.__new__(cls)

        # This is a local branch, see if it is a tracking branch or a local branch
        if refspec.startswith('refs/heads/'):
            remote = repo.configs.get('branch.%s.remote' % refspec.rpartition('/')[2], '.')
            remote = remote != '.' and remote or None
            if remote is None:
                cls = LocalBranch
            else:
                cls = TrackingBranch
        # This is a remote branch, see if it is a tracked branch or a published branch
        else:
            if refspec in repo.branch_parents.keys():
                cls = TrackedBranch
            else:
                cls = PublishedBranch
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        super(Branch, self).__init__(*args, **kwargs)
        self.parent_refspec = self.repo.branch_parents.get(self.refspec, self.refspec)
        # Find the common merge ancestor to show ahead/behind statistics.
        master_sha = self.repo.git('show', '--pretty=format:%H', self.repo.master).split('\n')[0].strip()
        self.merge_refspec = self.repo.git('merge-base', master_sha, self.sha, split=True)[0].strip()

    @property
    @memoize
    def pull(self):
        return bool(self.repo.git('log', '--pretty=format:%H', '%s..%s' % (self.refspec, self.parent_refspec), split=True))

    @property
    @memoize
    def push(self):
        return bool(self.repo.git('log', '--pretty=format:%H', '%s..%s' % (self.parent_refspec, self.refspec), split=True))

    @property
    @memoize
    def ahead(self):
        return len(self.repo.git('log', '--pretty=format:%H', '%s..%s' % (self.merge_refspec, self.refspec), split=True))

    @property
    @memoize
    def behind(self):
        # TODO: find a better way to determine how fare behind we are from our branch "parent"
        return len(self.repo.git('log', '--pretty=format:%H', '%s..%s' % (self.refspec, self.repo.master), split=True))

class LocalBranch(Branch):
    """
    A local branch that is not tracking a published branch.
    """
    @property
    def push(self):
        return False

    @property
    def pull(self):
        return False

class PublishedBranch(Branch):
    """
    A branch on a remote server that is not being tracked locally.
    """
    pass

class TrackingBranch(PublishedBranch):
    """
    A local branch that is tracking a published branch.
    """
    pass

class TrackedBranch(PublishedBranch):
    """
    A branch on a remote server that is being tracked locally.
    """
    pass

class Tag(Ref):
    pass

class Repository(object):
    def __init__(self, path=None):
        self.path = os.path.abspath(path or os.path.curdir)
        # Hack, make configurable
        self.master = 'master'

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
    @memoize
    def configs(self):
        return dict([ x.partition('=')[0::2] for x in self.git('config', '--list', split=True) ])

    def fetch(self):
        for remote in self.remotes():
            self.git('fetch', remote)
            self.git('fetch', '--tags', remote)

    @memoize
    def remotes(self):
        return self.git('remote', split=True)

    @memoize
    def refs(self):
        return [ Ref(self, *x.split()) for x in self.git('show-ref', split=True) ]

    @memoize
    def branches(self, *types):
        if types:
            return [ x for x in self.refs() if x.__class__ in types ]
        else:
            return [ x for x in self.refs() if isinstance(x, Branch) ]

    @memoize
    def tags(self):
        return [ x for x in self.refs() if isinstance(x, Tag) ]

    def branch(self):
        return self.git('symbolic-ref', 'HEAD').strip().split('/')[2]

    @property
    @memoize
    def branch_parents(self):
        parents = {}
        for branch_refspec in [ x.split()[1] for x in self.git('show-ref', '--heads', split=True) ]:
            branch_name = branch_refspec.split('/')[2]
            remote = self.configs.get('branch.%s.remote' % branch_name, '.')
            parent = self.configs.get('branch.%s.merge' % branch_name, '')
            if remote != '.' and parent:
                parent = 'refs/remotes/%s/%s' % (remote, parent.split('/')[2])
                parents[branch_refspec] = parent
                parents[parent] = branch_refspec
            else:
                parents[branch_refspec] = parent
        return parents
