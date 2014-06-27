__all__ = ['discover_title']


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
    <SeriesTitle name='Lost', season_number=1, episode_number=3, \
        episode_name='Tabula Rasa', year=2004, imdb_id='tt0411008'>
    >>> print discover_title("The.Matrix.1999.720p.HDDVD.DTS.x264-ESiR")
    <MovieTitle name='The Matrix', year=1999, imdb_id='tt0133093'>
    >>> print discover_title("the.big.bang.theory.s05e13.720p.hdtv.x264-orenji")
    <SeriesTitle name='The Big Bang Theory', \
        season_number=5, episode_number=13, \
        episode_name='The Recombination Hypothesis', \
        year=2012, imdb_id='tt0898266'>
    >>> discover_title("afjbsdjfbkjab asjdvadvad")
    None
    """
    pass