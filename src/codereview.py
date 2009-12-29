import subprocess
import sys

from git import Repository

try:
    from termcolor import colored
except ImportError:
    print 'You should run "pip install termcolor" to fully utilize these utilities.'

    def colored(text, *args, **kwargs):
        print text

CONTENT_LENGTHS = {}
def content_length(key, text=None):
    CONTENT_LENGTHS[key] = max(CONTENT_LENGTHS.get(key, 0), len(text or ''))
    return CONTENT_LENGTHS[key]

def get_status():
    repo = Repository()
    repo.fetch()
    branches = repo.branches('origin')
    tags = repo.tags()

    branches = filter(lambda x: x != 'master', branches)
    statuses = []

    for branch in branches:
        parent = 'staging'
        if branch in ('staging', 'master',):
            parent = 'master'

        color, status, extra = 'red', '?', ''

        if "%s-codereview" % branch not in tags:
            color, status = 'red', 'new'
            commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (parent, branch), split=True)
            if commits:
                extra = '%s commits' % len(commits)
        else:
            commits = repo.git('log', '--pretty=format:"- %s [%h]"', '%s-codereview..origin/%s' % (branch, branch), split=True)
            if commits:
                color, status = 'red', 'review'
                extra = '%s commits' % len(commits)
            else:
                commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (parent, branch), split=True)
                if commits:
                    color, status = 'yellow', 'merge'
                    extra = '%s commits' % len(commits)
                else:
                    color, status = 'green', 'done'

        statuses.append([status, color, branch, extra])
        content_length('status', status)
        content_length('branch', branch)

    for status, color, branch, extra in statuses:
        print '%s %s %s' % (colored('[ %s ]' % status.upper().rjust(content_length('status')), color), branch.ljust(content_length('branch')), extra and colored('(%s)' % extra, color, attrs=['reverse']) or '')

def complete_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    repo.git('tag', '-a', '%s-codereview' % branch, '-f', '-m', 'creating code review for branch %s' % branch)
    repo.git('push', '--tags')
    print 'Created tag %s-codereview' % branch
    repo.git('checkout', 'staging')
    print colored('Switched back to staging branch.', 'yellow')
