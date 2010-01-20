import subprocess
import sys

from gitgoggles.asciitable import AsciiTable, AsciiCell
from gitgoggles.git import Repository, TrackingBranch, LocalBranch, PublishedBranch, TrackedBranch
from gitgoggles.utils import colored

TAG_PREFIX = 'codereview--'

def get_status():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'True') != 'False':
        repo.fetch()

    refs = repo.branches(LocalBranch, TrackingBranch, PublishedBranch)
    tags = repo.tags()

    table = AsciiTable([u'Status', u'Branch', u'Review', u'Ahead', u'Behind', u'Pull', u'Push', u'Modified'])

    if repo.configs.get('gitgoggles.colors', 'True') == 'False':
        colored.disabled = True

    icons = {
        'unknown': repo.configs.get('gitgoggles.icons.unknown', u'\u203D'),
        'success': repo.configs.get('gitgoggles.icons.success', u'\u2714'),
        'failure': repo.configs.get('gitgoggles.icons.failure', u'\u2718'),
        }
    colors = {
        'local': repo.configs.get('gitgoggles.colors.local', 'cyan'),
        'new': repo.configs.get('gitgoggles.colors.new', 'red'),
        'review': repo.configs.get('gitgoggles.colors.review', 'red'),
        'merge': repo.configs.get('gitgoggles.colors.merge', 'yellow'),
        'done': repo.configs.get('gitgoggles.colors.done', 'green'),
        }

    for ref in refs:
        parent = ref.name in ('staging', 'master',) and 'master' or 'staging'
        codereview_tag = "%s%s" % (TAG_PREFIX, ref.shortname)

        color = 'red'
        status = u'?'
        review_commits = 0
        ahead_commits = ref.ahead
        behind_commits = ref.behind
        pull = ref.pull
        push = ref.push

        if ref.__class__ in (TrackingBranch, LocalBranch, TrackedBranch):
            if codereview_tag not in [ x.name for x in tags ]:
                review_commits = len(repo.git('log', '--pretty=format:%H', '%s..%s' % (ref.merge_refspec or '', ref.refspec), split=True))
            else:
                review_commits = len(repo.git('log', '--pretty=format:%H', '%s..%s' % (codereview_tag, ref.refspec), split=True))
        else:
            review_commits = None

        if ref.__class__ == LocalBranch:
            color, status = colors['local'], u'local'
        elif codereview_tag not in [ x.name for x in tags ]:
            color, status = colors['new'], u'new'
        else:
            if review_commits:
                color, status = colors['review'], u'review'
            else:
                if ahead_commits:
                    color, status = colors['merge'], u'merge'
                else:
                    color, status = colors['done'], u'done'

        review = bool(review_commits) or None
        ahead = bool(ahead_commits) or None
        behind = bool(behind_commits) or None
        tracked = ref.__class__ in (TrackingBranch, LocalBranch, TrackedBranch)

        review_text, review_color = review_commits is not None and (u'%s unreviewed' % review_commits, review and color) or (icons['unknown'], 'yellow',)
        ahead_text, ahead_color = ahead_commits is not None and (u'%s ahead' % ahead_commits, ahead and color) or (icons['unknown'], 'yellow',)
        behind_text, behind_color = behind_commits is not None and (u'%s behind' % behind_commits, behind and color) or (icons['unknown'], 'yellow',)

        pull_text, pull_color = not tracked and (icons['unknown'], 'yellow',) or (pull and (icons['failure'], 'red',) or (icons['success'], 'green',))
        push_text, push_color = not tracked and (icons['unknown'], 'yellow',) or (push and (icons['failure'], 'red',) or (icons['success'], 'green',))

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

    if repo.configs.get('gitgoggles.fetch', 'True') != 'False':
        repo.fetch()

    branch = repo.branch()
    repo.git('tag', '-a', '%s%s' % (TAG_PREFIX, branch), '-f', '-m', 'creating code review for branch %s' % branch)
    repo.git('push', '--tags')
    print 'Created tag %s%s' % (TAG_PREFIX, branch)
    repo.git('checkout', 'staging')
    print 'Switched back to staging branch.'

def start_review():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'True') != 'False':
        repo.fetch()

    branch = repo.branch()
    tags = repo.tags()

    parent = branch in ('staging', 'master',) and 'master' or 'staging'

    cr_tag = '%s%s' % (TAG_PREFIX, branch)

    if cr_tag in [ x.name for x in tags ]:
        repo.git('diff', '-w', '%s..%s' % (cr_tag, branch), join=True)
    else:
        repo.git('diff', '-w', '%s..%s' % (parent, branch), join=True)

def update_branches():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'True') != 'False':
        repo.fetch()

    branch = repo.branch()
    refs = repo.branches(TrackingBranch)
    for branch in refs:
        if branch.pull:
            repo.git('checkout', branch.name)
            repo.git('pull')

