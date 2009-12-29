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

    def status(text, color='red'):
        return colored('[ %s ]' % text.upper().rjust(6), color)

    for branch in branches:
        s = status('?')
        if "%s-codereview" % branch not in tags:
            s = status('new', 'red')
        else:
            output = repo.git('diff', '%s-codereview..%s' % (branch, branch))
            if output:
                s = status('review', 'red')
            else:
                if repo.git('diff', 'staging..%s' % branch):
                    s = status('merge', 'yellow')
                else:
                    s = status('done', 'green')

        print '%s %s' % (s, branch)

def complete_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    repo.git('tag', '-a', '%s-codereview' % branch, '-f', '-m', 'creating code review for branch %s' % branch)
    repo.git('push', '--tags')
    print 'created tag %s-codereview' % branch
