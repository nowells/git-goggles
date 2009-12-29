import subprocess
import sys

from git import Repository

try:
    from termcolor import colored
except ImportError:
    raise ImportError('You must run "pip install termcolor" to use this library')

def get_status():
    repo = Repository()
    repo.fetch()
    branches = repo.branches('origin')
    tags = repo.tags()

    branches = filter(lambda x: x != 'master', branches)

    for branch in branches:
        if "%s-codereview" % branch not in tags:
            print colored("%s needs to be reviewed (no tag)" % branch, 'red')
        else:
            output = repo.git('diff', '%s-codereview..%s' % (branch, branch))
            if output:
                print '%s needs to be reviewed:' % branch
            else:
                print colored('%s is already reviewed.' % branch, 'green')


def complete_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    repo.git('tag', '-a', '%s-codereview' % branch, '-f', '-m', 'creating code review for branch %s' % branch)
    repo.git('push', '--tags')
    print 'created tag %s-codereview' % branch
