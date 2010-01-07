import subprocess
import sys

from asciitable import AsciiTable, AsciiCell
from git import Repository, TrackingBranch, LocalBranch, PublishedBranch, TrackedBranch

def get_status():
    repo = Repository()
    repo.fetch()
    refs = repo.branches(LocalBranch, TrackingBranch, PublishedBranch)
    tags = repo.tags()

    TAG_PREFIX = 'codereview--'

    table = AsciiTable(['Status', 'Branch', 'Review', 'Ahead', 'Behind', 'Pull', 'Push', 'Modified'])

    for ref in refs:
        parent = ref.name in ('staging', 'master',) and 'master' or 'staging'
        codereview_tag = "%s%s" % (TAG_PREFIX, ref.shortname)

        color = 'red'
        status = '?'
        review_commits = 0
        ahead_commits = ref.ahead
        behind_commits = ref.behind
        pull = ref.pull
        push = ref.push

        if ref.__class__ == LocalBranch:
            color, status = 'blue', 'local'
            review_commits = 0
        elif codereview_tag not in [ x.name for x in tags ]:
            color, status = 'red', 'new'
            review_commits = ahead_commits
        else:
            review_commits = len(repo.git('log', '--pretty=format:"- %s [%h]"', '%s..%s' % (codereview_tag, ref.refspec), split=True))
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
        tracked = ref.__class__ in (TrackingBranch, LocalBranch, TrackedBranch)

        review_text, review_color = '%s unreviewed' % review_commits, review and color
        ahead_text, ahead_color = '%s ahead' % ahead_commits, ahead and color
        behind_text, behind_color = '%s behind' % behind_commits, behind and color

        pull_text, pull_color = not tracked and (u'\u203D', 'yellow',) or (pull and (u'\u2718', 'red',) or (u'\u2714', 'green',))
        push_text, push_color = not tracked and (u'\u203D', 'yellow',) or (push and (u'\u2718', 'red',) or (u'\u2714', 'green',))

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
