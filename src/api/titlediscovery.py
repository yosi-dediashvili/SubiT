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
    """
    pass