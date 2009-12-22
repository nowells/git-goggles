import subprocess
import sys

from git import get_current_branch, get_tags, get_branches

def get_status():
    branches = get_branches()
    tags = get_tags()

    branches = filter(lambda x: x != 'master', branches)

    for branch in branches:
        if "%s-codereview" % branch not in tags:
            print "%s needs to be reviewed (no tag)" % branch
        else:
            p = subprocess.Popen([
                'git',
                'diff',
                '%s-codereview..%s' % (branch, branch)
                ], stdout=subprocess.PIPE)
            output = p.communicate()[0]
            if output:
                print '%s needs to be reviewed with following diff:\n %s' % (branch, output)


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
