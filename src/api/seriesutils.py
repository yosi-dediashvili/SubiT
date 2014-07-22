import re

from utils import take_first, get_regex_match, get_regex_results


__all__ = ['is_series_query', 'remove_series_nubmering', 'get_series_numbering']

SERIES_REGEXES = [
    # foo.S03E12.HDTV or foo.s04.e15.HDTV
    r's(?P<season>\d{1,2})[ \-\.]?e(?P<episode>\d{1,2})',                                            
    # foo.Season.05.Episode.06.HDTV
    r'season[ \.\-\_]?(?P<season>\d{1,2})[ \.\-\_]?episode[ \.\-\_]?(?P<episode>\d{1,2})',   
    # foo.4x15.HDTV
    r'(?P<season>\d{1,2})x(?P<episode>\d{1,2})',
    # foo.415.HDTV, foo.105.HDTV
    r'(?<=[ \.\-\_])(?P<season>\d)(?P<episode>\d{2})(?=[ \.\-\_])'
]


def get_series_numbering(query):
    """ 
    Returns the parameters of a series, Season and Episode, the result is a 
    tuple of (Season, Episode), each item is an integer. The query is converted 
    to lower case before the search.

    >>> get_series_numbering("foo.s03e12.hdtv")
    (3, 12)
    >>> get_series_numbering("foo.season.3.episode.12.hdtv")
    (3, 12)
    >>> get_series_numbering("foo.3x12.hdtv")
    (3, 12)
    >>> get_series_numbering("foo.3x12.hdtv")
    (3, 12)
    >>> get_series_numbering("foo.312.hdtv")
    (3, 12)
    >>> get_series_numbering("foo.hdtv")
    ()
    >>> get_series_numbering("foo.1112.hdtv")
    ()
    """
    query = query.lower()
    result = []

    for regex in SERIES_REGEXES:
        # We might end up with result being None because takefirst returns None
        # if there are no items in an iterable.
        result = take_first(get_regex_results(regex, query, False))
        
        if result:
            # We convert result to list in order to change the items inside it
            result = list(result)
            # Convert to integers
            if result[0].isdigit():
                result[0] = int(result[0])
            if result[1].isdigit():
                result[1] = int(result[1])
            break
     
    # result might be None (as it's says earlier in the function), so we can
    # get exception if result is None and we try to convert it to tuple.
    if result is None:
        return tuple([])
    else:
        return tuple(result)

def get_series_numbering_string(query, season_number, episode_number):
    """
    Returns the string that specifies the series numbering in the query. 

    >>> get_series_numbering_string("foo.s03e12.hdtv", 3, 12)
    's03e12'
    >>> get_series_numbering_string("foo.3x12.hdtv", 3, 12)
    '3x12'
    >>> get_series_numbering_string("foo.season.3.episode.12.hdtv", 3, 12)
    'season.3.episode.12'
    >>> get_series_numbering_string("foo.312.hdtv", 3, 12)
    '312'
    >>> print get_series_numbering_string("foo.hdtv", 3, 12)
    None
    """
    numbering = get_series_numbering(query)
    if (not numbering or
        numbering[0] != season_number or 
        numbering[1] != episode_number):
        return None

    # Wrap the whole regex with brackets so we'll receive the whole string that
    # matched the regex. This means that for each pattern, we'll receive 3 
    # result. The first will be the string itself that matched, and the other
    # two will be the series numbering.
    wrapped_regex = map(lambda r: "(%s)" % r, SERIES_REGEXES)
    return get_regex_match(query, wrapped_regex)[0]