import subprocess
import sys

from git import get_current_branch, get_tags, get_branches
try:
    from termcolor import colored
except ImportError:
    raise ImportError('You must run "pip install termcolor" to use this library')


def get_status():
    branches = get_branches()
    tags = get_tags()

    for branch in branches:
        if "%s-codereview" % branch not in tags:
            print colored("%s needs to be reviewed (no tag)" % branch, 'red')
        else:
            p = subprocess.Popen([
                'git',
                'diff',
                '%s-codereview..%s' % (branch, branch)
                ], stdout=subprocess.PIPE)
            output = p.communicate()[0]
            if output:
                print '%s needs to be reviewed:' % branch
            else:
                print colored('%s is already reviewed.' % branch, 'green')


def complete_review():
    branch = get_current_branch()
    p = subprocess.Popen([
        'git',
        'tag',
        '-a',
        '%s-codereview' % branch,
        '-f',
        '-m',
        'creating code review for branch %s' % branch,
        ])
    p.communicate()
    print 'created tag %s-codereview' % branch
