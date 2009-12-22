import subprocess

def get_current_branch():
    p = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    return [line[2:] for line in output if line and line[0] == '*'][0]


def get_branches():
    p = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    return [line[2:] for line in output if line]


def get_tags():
    p = subprocess.Popen(['git', 'tag'], stdout=subprocess.PIPE)
    output = p.communicate()[0].split('\n')
    return filter(lambda x: x.endswith('-codereview'), output)
