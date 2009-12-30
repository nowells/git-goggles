import subprocess
import sys

from git import Repository

try:
    from termcolor import colored
except ImportError:
    print 'You should run "pip install termcolor" to fully utilize these utilities.'

    def colored(text, *args, **kwargs):
        return text

CONTENT_LENGTHS = {}
def content_length(key, text=None):
    CONTENT_LENGTHS[key] = max(CONTENT_LENGTHS.get(key, 0), len(text or ''))
    return CONTENT_LENGTHS[key]

def get_status():
    repo = Repository()
    repo.fetch()
    branches = repo.branches('origin')
    local_branches = repo.branches()
    tags = repo.tags()

    branch_states = []

    for branch in branches:
        parent = branch in ('staging', 'master',) and 'master' or 'staging'

        color, status, review_commits, ahead_commits, behind_commits, local_ahead_commits, local_behind_commits= 'red', '?', [], [], [], None, None

        ahead_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (parent, branch), split=True)
        behind_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (branch, parent), split=True)
        if branch in local_branches:
            local_ahead_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..%s' % (branch, branch), split=True)
            local_behind_commits = repo.git('log', '--pretty=format:"- %s [%h]"', '%s..origin/%s' % (branch, branch), split=True)

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
            'review_commits': review_commits,
            'ahead_commits': ahead_commits,
            'behind_commits': behind_commits,
            'local_ahead_commits': local_ahead_commits,
            'local_behind_commits': local_behind_commits,
            })

        # Track length of longest string for each column
        content_length('status', status)
        content_length('branch', branch)

    print u'|%s|%s|%s|%s|%s|%s|%s|' % (
        u' Status '.ljust(content_length('status', 'status') + len('  ')),
        u' Branch '.ljust(content_length('branch', 'branch') + len('  ')),
        u' Review '.ljust(16),
        u' Ahead '.ljust(11),
        u' Behind '.ljust(12),
        u' Pull ',
        u' Push ',
        )

    # Print out pretty upper container
    print '-%s-%s-%s-%s-%s-%s-%s-' % (
        u'-'.join([ u'' for x in range(content_length('status') + len('  ') + 1) ]),
        u'-'.join([ u'' for x in range(content_length('branch') + len('  ') + 1) ]),
        u'-'.join([ u'' for x in range(16 + 1) ]),
        u'-'.join([ u'' for x in range(11 + 1) ]),
        u'-'.join([ u'' for x in range(12 + 1) ]),
        u'-'.join([ u'' for x in range(6 + 1) ]),
        u'-'.join([ u'' for x in range(6 + 1) ]),
        )

    # Print out status for each branch
    for s in branch_states:
        review_commits = len(s['review_commits'])
        ahead_commits = len(s['ahead_commits'])
        behind_commits = len(s['behind_commits'])
        color = s['color']
        branch = s['branch']
        status = s['status']
        pull = bool(s['local_behind_commits'])
        push = bool(s['local_ahead_commits'])
        not_local = s['local_behind_commits'] is None

        print u'|%s|%s|%s|%s|%s|%s|%s|' % (
            colored(u' %s ' % status.upper().rjust(content_length('status')), color),
            u' %s ' % branch.ljust(content_length('branch')),
            colored((u' %s unreviewed ' % review_commits).rjust(16), review_commits and color or None, attrs=review_commits and ['reverse'] or []),
            colored((u' %s ahead ' % ahead_commits).rjust(11), ahead_commits and color or None, attrs=ahead_commits and ['reverse'] or []),
            colored((u' %s behind ' % behind_commits).rjust(12), behind_commits and color or None, attrs=behind_commits and ['reverse'] or []),
            not_local and colored(u'  \u2049   ', 'yellow') or (pull and colored(u'  \u2718   ', 'red') or colored(u'  \u2714   ', 'green')),
            not_local and colored(u'  \u2049   ', 'yellow') or (push and colored(u'  \u2718   ', 'red') or colored(u'  \u2714   ', 'green')),
            )

    # Print out pretty lower container
    print u'-%s-%s-%s-%s-%s-%s-%s-' % (
        u'-'.join([ u'' for x in range(content_length('status') + len('  ') + 1) ]),
        u'-'.join([ u'' for x in range(content_length('branch') + len('  ') + 1) ]),
        u'-'.join([ u'' for x in range(16 + 1) ]),
        u'-'.join([ u'' for x in range(11 + 1) ]),
        u'-'.join([ u'' for x in range(12 + 1) ]),
        u'-'.join([ u'' for x in range(6 + 1) ]),
        u'-'.join([ u'' for x in range(6 + 1) ]),
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

def start_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    tags = repo.tags()

    parent = branch in ('staging', 'master',) and 'master' or 'staging'

    cr_tag = '%s-codereview' % branch

    if cr_tag in tags:
        repo.git('diff', '-w', '%s..%s' % (cr_tag, branch), join=True)
    else:
        repo.git('diff', '-w', '%s..%s' % (parent, branch), join=True)
