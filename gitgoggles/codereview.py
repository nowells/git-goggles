import datetime
import subprocess
import sys

from gitgoggles.asciitable import AsciiTable, AsciiCell
from gitgoggles.git import Repository, TrackingBranch, LocalBranch, PublishedBranch, TrackedBranch
from gitgoggles.utils import colored, terminal_dimensions

TAG_PREFIX = 'codereview--'

def get_status():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'true') != 'false':
        repo.fetch()

    refs = repo.branches(LocalBranch, TrackingBranch, PublishedBranch)
    tags = repo.tags()

    BRANCH_WIDTH = repo.configs.get('gitgoggles.table.branch-width')
    LEFT_PADDING = repo.configs.get('gitgoggles.table.left-padding', 0)
    RIGHT_PADDING = repo.configs.get('gitgoggles.table.right-padding', 0)
    HORIZONTAL_RULE = repo.configs.get('gitgoggles.table.horizontal-rule', 'false') != 'false'

    TERMINAL_ROWS, TERMINAL_COLUMNS = terminal_dimensions()

    table = AsciiTable([
        AsciiCell('Status'),
        AsciiCell('Branch', width=BRANCH_WIDTH, resizable=True),
        AsciiCell('Review', align='right'),
        AsciiCell('Ahead', align='right'),
        AsciiCell('Behind', align='right'),
        AsciiCell('Pull'),
        AsciiCell('Push'),
        AsciiCell('Mod', align='right'),
        ], LEFT_PADDING, RIGHT_PADDING, HORIZONTAL_RULE, TERMINAL_COLUMNS)

    if repo.configs.get('gitgoggles.colors', 'true') == 'false':
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
        if repo.configs.get('gitgoggles.ignore.%s' % ref.shortname, 'false') == 'true':
            continue

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
                review_commits = len(repo.git('log', '--no-merges', '--pretty=format:%H', '%s..%s' % (ref.merge_refspec or '', ref.refspec), split=True))
            else:
                review_commits = len(repo.git('log', '--no-merges', '--pretty=format:%H', '%s..%s' % (codereview_tag, ref.refspec), split=True))
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

        review_text, review_color = review_commits is not None and (u'%s ahead' % review_commits, review and color) or (icons['unknown'], 'yellow',)
        ahead_text, ahead_color = ahead_commits is not None and (u'%s ahead' % ahead_commits, ahead and color) or (icons['unknown'], 'yellow',)
        behind_text, behind_color = behind_commits is not None and (u'%s behind' % behind_commits, behind and color) or (icons['unknown'], 'yellow',)

        pull_text, pull_color = not tracked and (icons['unknown'], 'yellow',) or (pull and (icons['failure'], 'red',) or (icons['success'], 'green',))
        push_text, push_color = not tracked and (icons['unknown'], 'yellow',) or (push and (icons['failure'], 'red',) or (icons['success'], 'green',))

        delta = datetime.date.today() - ref.modified.date()
        if delta <= datetime.timedelta(days=1):
            modified_color = 'cyan'
        elif delta <= datetime.timedelta(days=7):
            modified_color = 'green'
        elif delta < datetime.timedelta(days=31):
            modified_color = 'yellow'
        else:
            modified_color = 'red'

        table.add_row([
            AsciiCell(status.upper(), color),
            AsciiCell(ref.name, width=BRANCH_WIDTH, resizable=True),
            AsciiCell(review_text, review_color, reverse=review, align='right'),
            AsciiCell(ahead_text, ahead_color, reverse=ahead, align='right'),
            AsciiCell(behind_text, behind_color, reverse=behind, align='right'),
            AsciiCell(pull_text, pull_color, align='center'),
            AsciiCell(push_text, push_color, align='center'),
            AsciiCell(ref.timedelta, modified_color, align='right'),
            ])

    table.render()

def complete_review():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'true') != 'false':
        repo.fetch()

    branch = repo.branch()
    repo.git('tag', '-a', '%s%s' % (TAG_PREFIX, branch), '-f', '-m', 'creating code review for branch %s' % branch)
    print 'Created tag %s%s' % (TAG_PREFIX, branch)

def start_review():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'true') != 'false':
        repo.fetch()

    branch = repo.branch()
    tags = repo.tags()

    # TODO: remove assumption of base branch
    parent = branch in ('staging', 'master',) and 'master' or 'staging'

    cr_tag = '%s%s' % (TAG_PREFIX, branch)

    if cr_tag in [ x.name for x in tags ]:
        repo.git('diff', '-w', '%s..%s' % (cr_tag, branch), join=True)
    else:
        repo.git('diff', '-w', '%s..%s' % (parent, branch), join=True)

def update_branches():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'true') != 'false':
        repo.fetch()

    branch = repo.branch()
    refs = repo.branches(TrackingBranch)
    for branch in refs:
        if branch.pull:
            repo.git('checkout', branch.name)
            repo.git('pull')
