import logging
logger = logging.getLogger("subit.api.identifiersextractor")
import os

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
    >>> sorted(extract_identifiers(\
        title, ["The.Matrix.1999.720p.HDDVD.DTS.x264-ESiR"]))
    ['720p', 'dts', 'esir', 'hddvd', 'x264']
    >>> extract_identifiers(title, ["The.Matrix.1999"])
    []
    >>> extract_identifiers(title, ["The.Matrix"])
    []
    >>> sorted(extract_identifiers(title, ["720p.HDDVD.DTS"]))
    ['720p', 'dts', 'hddvd']
    >>> sorted(extract_identifiers(title, \
        ["The.Matrix.cd1.dvdrip.ac3", "The.Matrix.cd2.dvdrip.ac3"]))
    ['ac3', 'dvdrip']
    >>> sorted(extract_identifiers(title, \
        ["C:\\The.Matrix.1999.720p.dts\\movie.mkv"]))
    ['720p', 'dts']
    >>> sorted(extract_identifiers(title, \
        ["C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd1.mkv", \
        "C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd2.mkv"]))
    ['ac3', 'dvdrip', 'movie']
    >>> extract_identifiers(title, \
        ["C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd1.mkv", \
        "movie.cd2"])
    Traceback (most recent call last):
        ...
    InvalidQueriesValue: All the queries must be either full paths or simple.
    >>> sorted(extract_identifiers(title, \
        ["C:\\The.Matrix.1999.dvdrip.ac3.cd1\\movie.mkv", \
        "C:\\The.Matrix.1999.dvdrip.ac3.cd2\\movie.mkv"]))
    ['ac3', 'dvdrip']

    >>> title = SeriesTitle("The Big Bang Theory", 5, 13, "tt2139151", \
        "The Recombination Hypothesis", 2012, "tt0898266")
    >>> sorted(extract_identifiers(\
        title, ["the.big.bang.theory.s05e13.720p.hdtv.x264-orenji"]))
    ['720p', 'hdtv', 'orenji', 'x264']
    >>> title = SeriesTitle("The Big Bang Theory", 1, 4, "tt1091291", \
        "The Luminous Fish Effect", 2007, "tt0898266")
    >>> sorted(extract_identifiers(title, \
        ["The.Big.Bang.Theory.1x04.The.Luminous.Fish.Effect.720p.HDTV.AC3-CTU"]))
    ['720p', 'ac3', 'ctu', 'hdtv']
    >>> extract_identifiers(title, \
        ["The.Big.Bang.Theory.1x04.cd1", "The.Big.Bang.Theory.1x04.cd2"])
    Traceback (most recent call last):
        ...
    InvalidQueriesValue: Multiple queries is allowed only for MovieTitle.
    """
    
    logger.debug("extract_identifiers got called with title: {0} queries: {1}"
        .format(title, queries))

    identifiers = set()
    if isinstance(title, MovieTitle):
        extract_identifiers_func = extract_identifiers_movie
    else:
        extract_identifiers_func = extract_identifiers_series

    for formatted_queries in _yield_queries(queries):
        identifiers.update(extract_identifiers_func(title, formatted_queries))

    logger.debug("The identifiers are: %s" % identifiers)
    return list(identifiers)

def extract_identifiers_series(title, queries):
    if len(queries) != 1:
        raise InvalidQueriesValue(
            "Multiple queries is allowed only for MovieTitle.")

    from seriesutils import get_series_numbering_string
    series_numbering_string = get_series_numbering_string(
        queries[0], title.season_number, title.episode_number)

    normalized_title = title.name
    if title.episode_name:
        normalized_title += (" " + title.episode_name)
    if series_numbering_string:
        normalized_title += (" " + series_numbering_string)

    normalized_title = _normalize_query(normalized_title)
    return _extract_identifiers(normalized_title, queries)

def extract_identifiers_movie(title, queries):
    normalized_title = title.name
    if title.year:
        normalized_title += (" " + str(title.year))
    normalized_title = _normalize_query(normalized_title)
    return _extract_identifiers(normalized_title, queries)

def _normalize_query(query):
    """
    >>> _normalize_query("a.b.c.d.d.d_z")
    ['a', 'b', 'c', 'd', 'z']
    >>> _normalize_query("a")
    []
    """
    normalized_query = normalize_name(query)
    output = []
    # Skip the first normalization, because it's the original string.
    for normalization in normalized_query[1:]:
        for name in normalization.split("_"):
            if name not in output:
                output.append(name)
    return output

def _normalize_queries(queries):
    """
    Created a list of all the normalized string contained in all the queries 
    passed in the queries list.

    >>> sorted(_normalize_queries(["a.b.c.d", "a.b.c.e"]))
    ['a', 'b', 'c']
    """
    # Create a list that will contain all the normalized forms. 
    normalized_queries = set()

    for query in queries:
        normalized_query = set(_normalize_query(query))
        # If the set is empty, just put the result
        if not normalized_queries:
            normalized_queries.update(normalized_query)
        else:
            normalized_queries.intersection_update(normalized_query)

    return list(normalized_queries)

def _yield_queries(queries):
    """
    >>> list(_yield_queries(["abc"]))
    [['abc']]
    >>> sorted(list(_yield_queries(["C:\\\\bla\\\\abc"]))[:2])
    [['abc'], ['bla']]
    """
    # Make sure that they all either full paths or just names
    full_paths = filter(lambda q: os.path.isabs(q), queries)
    if full_paths and full_paths != queries:
        raise InvalidQueriesValue(
            "All the queries must be either full paths or simple.")

    if full_paths:
        # First, yield the file names
        files_names = \
            map(lambda p: os.path.splitext(os.path.basename(p))[0], full_paths)
        yield files_names

        # Then, yield the directories
        directories_names = \
            map(lambda p: os.path.basename(os.path.dirname(p)), queries)
        yield directories_names

        # Finally, if we got called for the 3rd time, use the hash
        yield _get_release_name_using_opensubtitles_hash(queries)
    else:
        yield queries

def _get_release_name_using_opensubtitles_hash(files_paths):
    return []

def _extract_identifiers(normalized_title, queries):
    """
    # The mcmxcix is 1999 in latin.
    >>> normalized_title = ["the", "matrix", "1999", 'mcmxcix']
    >>> ids = _extract_identifiers(\
        normalized_title, ["the.matrix.1999.720p.dts"])
    >>> sorted(ids)
    ['720p', 'dts']
    """
    normalized_query = _normalize_queries(queries)
    return list(set(normalized_query).difference(set(normalized_title)))