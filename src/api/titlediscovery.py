import logging
logger = logging.getLogger("subit.api.titlediscovery")
import os

from api.exceptions import FilePathDoesNotExists
from api.providers import get_provider_instance
from api.providers import ProvidersNames
from api.languages import Languages


__all__ = ['discover_title']

opensubtitles_provider = \
    get_provider_instance(ProvidersNames.OPEN_SUBTITLES, [Languages.ENGLISH])


def discover_title(query):
    """
    Tries to discover the title standing behind the query given. The query might
    be just some string, or a full path to a movie/series files.

    If the query is just a string, then we'll try only the simple method for the
    extraction. That is, sending the query as-is to OpenSubtitles. Otherwise, if
    it's a full path to a file, will use all the three methods (file name, hash 
    and directory name).

    If the function succeeds in discovering the title, a Title instance of the
    appropriate kind is returned (Movie or Series Title). If not, None is 
    returned.

    >>> print discover_title("The Matrix")
    <MovieTitle name='The Matrix', year=1999, imdb_id='tt0133093'>
    >>> print discover_title("Lost S01E03")
    <SeriesTitle name='Lost', episode_imdb_id='tt0636294', season_number=1, \
        episode_number=3, episode_name='Tabula Rasa', year=2004, \
        imdb_id='tt0411008'>
    >>> print discover_title("The.Matrix.1999.720p.HDDVD.DTS.x264-ESiR")
    <MovieTitle name='The Matrix', year=1999, imdb_id='tt0133093'>
    >>> print discover_title("the.big.bang.theory.s05e13.720p.hdtv.x264-orenji")
    <SeriesTitle name='The Big Bang Theory', \
        episode_imdb_id='tt2139151', season_number=5, episode_number=13, \
        episode_name='The Recombination Hypothesis', \
        year=2012, imdb_id='tt0898266'>
    >>> print discover_title("afjbsdjfbkjab asjdvadvad")
    None
    >>> discover_title(r"M:\\No such dir\\No.Such.File.mkv")
    Traceback (most recent call last):
        ...
    FilePathDoesNotExists: 'M:\\No such dir\\No.Such.File.mkv'
    """
    logger.debug("Discovering title for: %s" % query)

    if os.path.isabs(query):
        if os.path.exists(query):
            logger.debug("The query seems to be a file path")
            return discover_title_from_file_path(query)
        else:
            raise FilePathDoesNotExists("'%s'" % query)
    else:
        logger.debug("The query seems just a query")
        return discover_title_from_query(query)

def discover_title_from_file_path(file_path):
    file_hash = opensubtitles_provider.calculate_file_hash(file_path)
    title = opensubtitles_provider.get_title_by_hash(file_hash)
    logger.debug("Title by hash is: %s" % title)
    if title:
        return title

    file_name = os.path.splitext(os.path.basename(file_path))[0]
    title = discover_title_from_query(file_name)
    logger.debug("Title by file name is: %s" % title)
    if title:
        return title

    directory_name = os.path.basename(os.path.dirname(file_path))
    title = discover_title_from_query(directory_name)
    logger.debug("Title by directory name is: %s" % title)
    return title

def discover_title_from_query(query):
    title = opensubtitles_provider.get_title_by_query(query)
    logger.debug("Title by query is: %s" % title)
    return title