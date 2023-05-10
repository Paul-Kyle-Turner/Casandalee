import re


def build_link(link, index=None):
    starting = 'https://2e.aonprd.com/'
    starting_compile = re.compile(starting)
    last_digit = link[-1]
    if re.match(r'[0-9]', last_digit):
        if re.search(starting_compile, link):
            return link
        else:
            return starting + link
    if index is not None:
        if re.search(starting_compile, link):
            return link + index
        else:
            return starting + link + index

