import re


__all__ = ['get_regex_results', 'take_first', 'get_regex_match']


def get_regex_match(input_string, patterns):
    """
    Searches for the patterns in input_string, and return the first substring in 
    the input that matches one of the patterns. Returns None when nothing 
    matches.

    >>> get_regex_match("12345", ["^\d\d", "\d\d$"])
    '12'
    >>> print get_regex_match("12345", ["[^\d]", "^\d{4}$"])
    None
    """
    for pattern in patterns:
        results = re.findall(pattern, input_string)
        if results:
            return results[0]
    return None

def get_regex_results(pattern, content, with_groups = False):
    """ 
    Query the content and returns list of all result, in case of multi-group 
    pattern, will return a list of tuples (tuple for each group).

    >>> sorted(get_regex_results("\d", "1.2.3"))
    ['1', '2', '3']
    >>> sorted(get_regex_results("(\d)\.(\d)", "1.2.3.4"))
    [('1', '2'), ('3', '4')]
    >>> result = get_regex_results("(?P<first>\d)\.(?P<second>\d)", "1.2", True)
    >>> [{'first' : '1', 'second' : '2'}] == result
    True
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