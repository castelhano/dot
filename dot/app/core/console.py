import re

def Run(script):
    rows = script.split('\n')
    # attr_string = re.search('{(.*)}', script).group(1)
    # attr = attr_string.split(' ')
    return rows