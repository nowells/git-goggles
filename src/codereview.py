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
    branch_states = []

    for branch in branches:
        parent = branch in ('staging', 'master',) and 'master' or 'staging'

        color, status, review_commits, ahead_commits, behind_commits = 'red', '?', [], [], []

        ahead_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (parent, branch), split=True)
        behind_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (branch, parent), split=True)

        if "%s-codereview" % branch not in tags:
            color, status = 'red', 'new'
            review_commits = ahead_commits
        else:
            review_commits = repo.git('log', '--pretty=format:"- %s [%h]"', '%s-codereview..origin/%s' % (branch, branch), split=True)
            if review_commits:
                color, status = 'red', 'review'
            else:
                if ahead_commits:
                    color, status = 'yellow', 'merge'
                else:
                    color, status = 'green', 'done'

        branch_states.append({
            'status': status,
            'color': color,
            'branch': branch,
            'ahead_commits': ahead_commits,
            'behind_commits': behind_commits,
            'review_commits': review_commits,
            })

        # Track length of longest string for each column
        content_length('status', status)
        content_length('branch', branch)

    # Print out pretty upper container
    print '-%s-%s-%s-%s-%s-' % (
        '-'.join([ '' for x in range(content_length('status') + len('  ') + 1) ]),
        '-'.join([ '' for x in range(content_length('branch') + len('  ') + 1) ]),
        '-'.join([ '' for x in range(16 + 1) ]),
        '-'.join([ '' for x in range(11 + 1) ]),
        '-'.join([ '' for x in range(12 + 1) ]),
        )

    # Print out status for each branch
    for s in branch_states:
        review_commits = len(s['review_commits'])
        ahead_commits = len(s['ahead_commits'])
        behind_commits = len(s['behind_commits'])
        color = s['color']
        branch = s['branch']
        status = s['status']

        print '|%s|%s|%s|%s|%s|' % (
            colored(' %s ' % status.upper().rjust(content_length('status')), color),
            ' %s ' % branch.ljust(content_length('branch')),
            colored((' %s unreviewed ' % review_commits).rjust(16), review_commits and color or None, attrs=review_commits and ['reverse'] or []),
            colored((' %s ahead ' % ahead_commits).rjust(11), ahead_commits and color or None, attrs=ahead_commits and ['reverse'] or []),
            colored((' %s behind ' % behind_commits).rjust(12), behind_commits and color or None, attrs=behind_commits and ['reverse'] or []),
            )

    # Print out pretty lower container
    print '-%s-%s-%s-%s-%s-' % (
        '-'.join([ '' for x in range(content_length('status') + len('  ') + 1) ]),
        '-'.join([ '' for x in range(content_length('branch') + len('  ') + 1) ]),
        '-'.join([ '' for x in range(16 + 1) ]),
        '-'.join([ '' for x in range(11 + 1) ]),
        '-'.join([ '' for x in range(12 + 1) ]),
        )


def complete_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    repo.git('tag', '-a', '%s-codereview' % branch, '-f', '-m', 'creating code review for branch %s' % branch)
    repo.git('push', '--tags')
    print 'Created tag %s-codereview' % branch
    repo.git('checkout', 'staging')
    print colored('Switched back to staging branch.', 'yellow')
