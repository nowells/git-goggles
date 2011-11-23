import datetime
import subprocess
import itertools
import sys

from gitgoggles.asciitable import AsciiTable, AsciiCell
from gitgoggles.git import Repository, TrackingBranch, LocalBranch, PublishedBranch, TrackedBranch
from gitgoggles.utils import colored, terminal_dimensions, console
from gitgoggles.progress import handler

def get_status():
    repo = Repository()

    console(colored('# Working Tree: ', 'magenta'))
    console(colored(repo.branch(), 'cyan'))
    console(u'\n')

    uncommitted, changed, untracked, stashed = repo.status()
    if uncommitted or changed or untracked or stashed:
        table = AsciiTable(['', ''], 2, 0, False, border_characters=[u'', u'', u''])

        if uncommitted:
            table.add_row([
                AsciiCell('Uncommitted', 'green'),
                AsciiCell(str(len(uncommitted)), align='right'),
                ])

        if changed:
            table.add_row([
                AsciiCell('Changed', 'red'),
                AsciiCell(str(len(changed)), align='right'),
                ])

        if untracked:
            table.add_row([
                AsciiCell('Untracked', 'yellow'),
                AsciiCell(str(len(untracked)), align='right'),
                ])

        if stashed:
            table.add_row([
                AsciiCell('Stashed', 'cyan'),
                AsciiCell(str(len(stashed)), align='right'),
                ])

        table.render()

    console('\n')

    handler.uncapture_stdout()
    handler.capture_stdout()

    if repo.configs.get('gitgoggles.fetch', 'true') != 'false':
        repo.fetch()

    git_refs = repo.branches(LocalBranch, TrackingBranch, PublishedBranch)
    tags = repo.tags()

    BRANCH_WIDTH = repo.configs.get('gitgoggles.table.branch-width')
    LEFT_PADDING = repo.configs.get('gitgoggles.table.left-padding', 0)
    RIGHT_PADDING = repo.configs.get('gitgoggles.table.right-padding', 0)
    HORIZONTAL_RULE = repo.configs.get('gitgoggles.table.horizontal-rule', 'false') != 'false'

    TERMINAL_ROWS, TERMINAL_COLUMNS = terminal_dimensions()

    table = AsciiTable([
        AsciiCell('Branch', width=BRANCH_WIDTH, resizable=True),
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

    git_type = lambda x: x.__class__
    sorted(git_refs, key=git_type)

    for ref_type, refs in itertools.groupby(git_refs, git_type):
        for ref in refs:
            if repo.configs.get('gitgoggles.ignore.%s' % ref.shortname, 'false') == 'true':
                continue

            color = 'red'
            ahead_commits = ref.ahead
            behind_commits = ref.behind
            pull = ref.pull
            push = ref.push

            if ref.__class__ == LocalBranch:
                color = colors['local']
            else:
                if ahead_commits:
                    color = colors['merge']
                else:
                    color = colors['done']

            ahead = bool(ahead_commits) or None
            behind = bool(behind_commits) or None
            tracked = ref.__class__ in (TrackingBranch, LocalBranch, TrackedBranch)

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

            ahead_color = behind_color = modified_color

            table.add_row([
                AsciiCell(ref.name, width=BRANCH_WIDTH, resizable=True),
                AsciiCell(ahead_text, ahead_color, reverse=ahead, align='right'),
                AsciiCell(behind_text, behind_color, reverse=behind, align='right'),
                AsciiCell(pull_text, pull_color, align='center'),
                AsciiCell(push_text, push_color, align='center'),
                AsciiCell(ref.timedelta, modified_color, align='right'),
                ])

    table.render()

def update_branches():
    repo = Repository()

    if repo.configs.get('gitgoggles.fetch', 'true') != 'false':
        repo.fetch()

    branch = repo.branch()
    refs = repo.branches(TrackingBranch)
    for branch in refs:
        if branch.pull:
            repo.shell('git', 'checkout', branch.name)
            repo.shell('git', 'pull')
