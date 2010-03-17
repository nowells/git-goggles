import datetime
import os
import subprocess

from gitgoggles.progress import log
from gitgoggles.utils import AccumulatorDict, memoize, force_unicode, force_str, console

def log_activity(func):
    def _(self, *args, **kwargs):
        log.info('Processing %s' % self.shortname)
        return func(self, *args, **kwargs)
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

    def modified(self):
        timestamp = float(self.repo.git('log', '-1', '--pretty=format:%at', self.sha).split('\n')[0].strip())
        return datetime.datetime.fromtimestamp(timestamp)
    modified = property(log_activity(memoize(modified)))

    def timedelta(self):
        delta = datetime.datetime.now() - self.modified
        if delta.days > 365:
            return '-%sy' % round(delta.days / 365.0, 1)
        elif delta.days >= 1:
            return '-%sd' % delta.days
        elif delta.seconds >= 3600:
            return '-%sh' % (delta.seconds / 3600)
        else:
            return '-%sm' % (delta.seconds / 60)
    timedelta = property(timedelta)

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
        log.info('Processing %s' % self.shortname)
        # TODO: find a better way to determine parent refspec
        # Find the common merge ancestor to show ahead/behind statistics.
        self.merge_refspec = None
        if self.repo.master_sha:
            merge_refspec = self.repo.git('merge-base', self.repo.master_sha, self.sha, split=True)
            if merge_refspec:
                self.merge_refspec = merge_refspec[0].strip()

    def pull(self):
        return bool(self.repo.git('log', '--pretty=format:%H', '%s..%s' % (self.refspec, self.parent_refspec), split=True))
    pull = property(log_activity(memoize(pull)))

    def push(self):
        return bool(self.repo.git('log', '--pretty=format:%H', '%s..%s' % (self.parent_refspec, self.refspec), split=True))
    push = property(log_activity(memoize(push)))

    def ahead(self):
        if self.merge_refspec:
            return len(self.repo.git('log', '--no-merges', '--pretty=format:%H', '%s..%s' % (self.merge_refspec, self.refspec), split=True))
        return None
    ahead = property(log_activity(memoize(ahead)))

    def behind(self):
        if self.merge_refspec:
            # TODO: find a better way to determine how fare behind we are from our branch "parent"
            return len(self.repo.git('log', '--no-merges', '--pretty=format:%H', '%s..%s' % (self.refspec, self.repo.master), split=True))
        return None
    behind = property(log_activity(memoize(behind)))

class LocalBranch(Branch):
    """
    A local branch that is not tracking a published branch.
    """
    def push(self):
        return False
    push = property(push)

    def pull(self):
        return False
    pull = property(pull)

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
        master_sha = self.git('log', '-1', '--pretty=format:%H', self.master).split('\n')
        self.master_sha = master_sha and master_sha[0].strip() or ''

    def git(self, *args, **kwargs):
        split = kwargs.pop('split', False)
        join = kwargs.pop('join', False)

        command = ['git'] + list(args)

        log.debug(' '.join(command))

        if join:
            p = subprocess.Popen(command)
            p.communicate()
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            (stdout, stderr) = p.communicate(None)
            stdout = force_unicode(stdout)
            stderr = force_unicode(stderr)
            if split:
                stdout = filter(lambda x: x, map(lambda x: x.strip(), stdout.split(u'\n')))
            return stdout

    def configs(self):
        return dict([ x.partition('=')[0::2] for x in self.git('config', '--list', split=True) ])
    configs = property(memoize(configs))

    def fetch(self):
        for remote in self.remotes():
            log.info('Fetching %s' % remote)
            self.git('fetch', remote)
            self.git('fetch', '--tags', remote)

    def remotes(self):
        return self.git('remote', split=True)
    remotes = memoize(remotes)

    def refs(self):
        return [ Ref(self, *x.split()) for x in self.git('show-ref', split=True) ]
    refs = memoize(refs)

    def branches(self, *types):
        if types:
            return [ x for x in self.refs() if x.__class__ in types ]
        else:
            return [ x for x in self.refs() if isinstance(x, Branch) ]
    branches = memoize(branches)

    def tags(self):
        return [ x for x in self.refs() if isinstance(x, Tag) ]
    tags = memoize(tags)

    def branch(self):
        return self.git('symbolic-ref', 'HEAD').strip().split('/')[2]

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
    branch_parents = property(memoize(branch_parents))
