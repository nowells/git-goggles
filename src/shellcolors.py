NO_COLOR = r'\[\033[00m\]'
BOLD = r'\[\033[01m\]'
BLINK = r'\[\033[05m\]'
REVERSE = r'\[\033[07m\]'

COLORS = {
    # Dark foreground colors are constructed like \033[(X+30)m
    # Light foreground colors are constructed like \033[01;(X+30)m
    # Dark background colors are constructed like \033[(X+40)m
    # Light background colors are constructed like \033[01;(X+40)m
    'black': 0,    # darkgray
    'red': 1,
    'green': 2,
    'brown': 3,    # yellow
    'blue': 4,
    'purple': 5,
    'cyan': 6,
    'lightgray': 7, # white
    }

def fgcolor(text, color=None, light=False):
    color_string = ''
    if color in COLORS:
        color_string = r'\[\033[%s%sm\]' % (
            light and '1;' or '0;',
            COLORS[color] + 30
            )
    if text:
        return '%s%s%s' % (color_string, text, NO_COLOR)
    return text

def bgcolor(text, color=None, light=False):
    color_string = ''
    if color in COLORS:
        color_string = r'\[\033[%s%sm\]' % (
            light and '1;' or '0;',
            COLORS[color] + 40
            )
    if text:
        return '%s%s%s' % (color_string, text, NO_COLOR)
    return text
