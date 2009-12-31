import subprocess
import sys

from asciitable import AsciiTable, AsciiCell
from git import Repository

def get_status():
    repo = Repository()
    repo.fetch()
    refs = repo.branches('origin')
    local_refs = repo.branches()
    tags = repo.tags('origin')

    TAG_PREFIX = 'codereview--'

    table = AsciiTable(['Status', 'Branch', 'Review', 'Ahead', 'Behind', 'Pull', 'Push', 'Modified'])

    for ref in refs:
        parent = ref.name in ('staging', 'master',) and 'master' or 'staging'

        color, status, review_commits, ahead_commits, behind_commits, local_ahead_commits, local_behind_commits= 'red', '?', [], [], [], None, None

        ahead_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (parent, ref.name), split=True)
        behind_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..origin/%s' % (ref.name, parent), split=True)
        if ref.name in [ x.name for x in local_refs ]:
            local_ahead_commits = repo.git('log', '--pretty=format:"- %s [%h]"', 'origin/%s..%s' % (ref.name, ref.name), split=True)
            local_behind_commits = repo.git('log', '--pretty=format:"- %s [%h]"', '%s..origin/%s' % (ref.name, ref.name), split=True)

        if "%s%s" % (TAG_PREFIX, ref.name) not in [ x.name for x in tags ]:
            color, status = 'red', 'new'
            review_commits = ahead_commits
        else:
            review_commits = repo.git('log', '--pretty=format:"- %s [%h]"', '%s%s..origin/%s' % (TAG_PREFIX, ref.name, ref.name), split=True)
            if review_commits:
                color, status = 'red', 'review'
            else:
                if ahead_commits:
                    color, status = 'yellow', 'merge'
                else:
                    color, status = 'green', 'done'

        review = bool(review_commits) or None
        ahead = bool(ahead_commits) or None
        behind = bool(behind_commits) or None
        pull = bool(local_behind_commits) or None
        push = bool(local_ahead_commits) or None
        not_local = local_behind_commits is None

        review_text, review_color = '%s unreviewed' % len(review_commits), review and color
        ahead_text, ahead_color = '%s ahead' % len(ahead_commits), ahead and color
        behind_text, behind_color = '%s behind' % len(behind_commits), behind and color

        pull_text, pull_color = not_local and (u'\u2049', 'yellow',) or (pull and (u'\u2718', 'red',) or (u'\u2714', 'green',))
        push_text, push_color = not_local and (u'\u2049', 'yellow',) or (push and (u'\u2718', 'red',) or (u'\u2714', 'green',))

        table.add_row([
            AsciiCell(status.upper(), color),
            AsciiCell(ref.name),
            AsciiCell(review_text, review_color, reverse=review),
            AsciiCell(ahead_text, ahead_color, reverse=ahead),
            AsciiCell(behind_text, behind_color, reverse=behind),
            AsciiCell(pull_text, pull_color),
            AsciiCell(push_text, push_color),
            AsciiCell(ref.modified),
            ])

    table.render()

def complete_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    repo.git('tag', '-a', '%s%s' % (TAG_PREFIX, branch), '-f', '-m', 'creating code review for branch %s' % branch)
    repo.git('push', '--tags')
    print 'Created tag %s%s' % (TAG_PREFIX, branch)
    repo.git('checkout', 'staging')
    print 'Switched back to staging branch.'

def start_review():
    repo = Repository()
    repo.fetch()
    branch = repo.branch()
    tags = repo.tags()

    parent = branch in ('staging', 'master',) and 'master' or 'staging'

    cr_tag = '%s%s' % (TAG_PREFIX, branch)

    if cr_tag in [ x.name for x in tags ]:
        repo.git('diff', '-w', '%s..%s' % (cr_tag, branch), join=True)
    else:
        repo.git('diff', '-w', '%s..%s' % (parent, branch), join=True)
