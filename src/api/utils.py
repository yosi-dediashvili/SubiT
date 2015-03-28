import re


__all__ = [
    'get_regex_results', 'take_first', 'get_regex_match', 'strip_white_spaces'
]

WHITE_SPACES_RE = re.compile("[\r\t\n]")


def strip_white_spaces(input_string):
    """
    Stripes away any whitespace that is not a single space from the input
    string.

    >>> print strip_white_spaces("Some String\\tWith Tabs")
    Some StringWith Tabs
    >>> print strip_white_spaces("Some String\\r\\nWith NewLines")
    Some StringWith NewLines
    >>> print strip_white_spaces("Some String With Only Single Spaces")
    Some String With Only Single Spaces
    """
    return WHITE_SPACES_RE.sub("", input_string)

def get_regex_match(input_string, patterns):
    """
    Searches for the patterns in input_string, and return the first substring in
    the input that matches one of the patterns. Returns None when nothing
    matches.

    >>> get_regex_match("12345", ["^\d\d", "\d\d$"])
    '12'
    >>> print get_regex_match("12345", ["[^\d]", "^\d{4}$"])
    None
    >>> get_regex_match("12345", "^\d{3}")
    '123'
    """
    patterns = [patterns] if isinstance(patterns, str) else patterns
    for pattern in patterns:
        results = re.findall(pattern, input_string)
        if results:
            return results[0]
    return None

def get_regex_results(content, pattern, with_groups = False):
    """
    Query the content and returns list of all result, in case of multi-group
    pattern, will return a list of tuples (tuple for each group). pattern may
    be either a string or a compiled pattern.

    >>> sorted(get_regex_results("1.2.3", "\d"))
    ['1', '2', '3']
    >>> sorted(get_regex_results("1.2.3.4", "(\d)\.(\d)"))
    [('1', '2'), ('3', '4')]
    >>> result = get_regex_results("1.2", "(?P<first>\d)\.(?P<second>\d)", True)
    >>> [{'first' : '1', 'second' : '2'}] == result
    True
    >>> import re
    >>> pattern = re.compile("\d")
    >>> sorted(get_regex_results("1.2.3", pattern))
    ['1', '2', '3']
    """
    c_pattern = re.compile(pattern)
    if with_groups:
        return map(lambda i: i.groupdict(), c_pattern.finditer(content))

    return c_pattern.findall(content)

def take_first(items):
    """
    Function to return the first item in a list (will try to convert the
    parameter to list if it's not. return None on failure.

    >>> take_first([1, 2, 3])
    1
    >>> print take_first([])
    None
    """
    first_item = None
    try:
        if not isinstance(items, list):
            items = list(items)
        if items:
            first_item = items[0]
    except:
        pass
    return first_item