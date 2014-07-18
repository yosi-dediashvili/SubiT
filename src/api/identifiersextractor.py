import logging
logger = logging.getLogger("subit.api.identifiersextractor")

from exceptions import InvalidQueriesValue
from title import SeriesTitle
from title import MovieTitle
from namenormalization import normalize_name


__all__ = ['extract_identifiers']


def extract_identifiers(title, queries):
    """
    Extracts any string from queries that is not part of the title. If title is 
    a MovieTitle, the queries is allowed to be a list with more than one item.
    In case of SeriesTitle, the list must be one item long.

    >>> from title import MovieTitle, SeriesTitle
    >>> title = MovieTitle("The Matrix", 1999)
    >>> ids = extract_identifiers(\
        title, ["The.Matrix.1999.720p.HDDVD.DTS.x264-ESiR"])
    >>> sorted(ids)
    ['720p', 'dts', 'esir', 'hddvd', 'x264']
    >>> extract_identifiers(title, ["The.Matrix.1999"])
    []
    >>> extract_identifiers(title, ["The.Matrix"])
    []
    >>> ids = extract_identifiers(title, ["720p.HDDVD.DTS"])
    >>> sorted(ids)
    ['720p', 'dts', 'hddvd']
    >>> ids = extract_identifiers(title, \
        ["The.Matrix.cd1.dvdrip.ac3", "The.Matrix.cd2.dvdrip.ac3"])
    >>> sorted(ids)
    ['ac3', 'dvdrip']
    >>> ids = extract_identifiers(title, \
        ["C:\\The.Matrix.1999.720p.dts\\movie.mkv"])
    >>> sorted(ids)
    ['720p', 'dts']
    >>> ids = extract_identifiers(title, \
        ["C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd1.mkv", \
        "C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd2.mkv"])
    >>> sorted(ids)
    ['dvdrip', 'ac3']

    >>> title = SeriesTitle("The Big Bang Theory", 5, 13, "tt2139151", \
        "The Recombination Hypothesis", 2012, "tt0898266")
    >>> ids = extract_identifiers(\
        title, ["the.big.bang.theory.s05e13.720p.hdtv.x264-orenji"])
    >>> sorted(ids)
    ['720p', 'hdtv', 'orenji', 'x264']
    >>> title = SeriesTitle("The Big Bang Theory", 1, 4, "tt1091291", \
        "The Luminous Fish Effect", 2007, "tt0898266")
    >>> ids = extract_identifiers(title, \
        ["The.Big.Bang.Theory.1x04.The.Luminous.Fish.Effect.720p.HDTV.AC3-CTU"])
    >>> sorted(ids)
    ['720p', 'ac3', 'ctu', 'hdtv']
    >>> extract_identifiers(title, \
        ["The.Big.Bang.Theory.1x04.cd1", "The.Big.Bang.Theory.1x04.cd2"])
    Traceback (most recent call last):
        ...
    InvalidQueriesValue: Multiple queries is allowed only for MovitTitle.
    """
    
    logger.debug("extract_identifiers got called with title: {0} queries: {1}"
        .format(title, queries))

    if isinstance(title, MovieTitle):
        idetifiers = extract_identifiers_movie(title, queries)
    else:
        idetifiers = extract_identifiers_series(title, queries)

    logger.debug("The identifiers are: %s" % idetifiers)
    return idetifiers

def _extract_identifiers(normalized_title, queries):
    """
    # The mcmxcix is 1999 in latin.
    >>> normalized_title = ["the", "matrix", "1999", 'mcmxcix']
    >>> ids = _extract_identifiers(\
        normalized_title, ["the.matrix.1999.720p.dts"])
    >>> sorted(ids)
    ['720p', 'dts']
    """
    normalized_query = normalize_queries(queries)
    return list(set(normalized_query).difference(set(normalized_title)))

def extract_identifiers_series(title, queries):
    if len(queries) != 1:
        raise InvalidQueriesValue(
            "Multiple queries is allowed only for MovitTitle.")

    from seriesutils import get_series_numbering_string
    series_numbering_string = get_series_numbering_string(
        queries[0], title.season_number, title.episode_number)

    normalized_title = title.name
    if title.episode_name:
        normalized_title += (" " + title.episode_name)
    if series_numbering_string:
        normalized_title += (" " + series_numbering_string)

    normalized_title = normalize_query(normalized_title)
    return _extract_identifiers(normalized_title, queries)

def extract_identifiers_movie(title, queries):
    normalized_title = title.name
    if title.year:
        normalized_title += (" " + str(title.year))
    normalized_title = normalize_query(normalized_title)
    return _extract_identifiers(normalized_title, queries)

def normalize_query(query):
    """
    >>> normalize_query("a.b.c.d.d.d_z")
    ['a', 'b', 'c', 'd', 'z']
    """
    normalized_query = normalize_name(query)
    output = []
    # Skip the first normalization, because it's the original string.
    for normalization in normalized_query[1:]:
        for name in normalization.split("_"):
            if name not in output:
                output.append(name)
    return output

def normalize_queries(queries):
    """
    Created a list of all the normalized string contained in all the queries 
    passed in the queries list.

    >>> sorted(normalize_queries(["a.b.c.d", "a.b.c.e"]))
    ['a', 'b', 'c']
    """
    # Create a list that will contain all the normalized forms. 
    normalized_queries = set()

    for query in queries:
        normalized_query = set(normalize_query(query))
        # If the set is empty, just put the result
        if not normalized_queries:
            normalized_queries.update(normalized_query)
        else:
            normalized_queries.intersection_update(normalized_query)

    return list(normalized_queries)