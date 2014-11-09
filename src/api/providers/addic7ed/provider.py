import logging
logger = logging.getLogger("subit.api.providers.addic7ed.provider")

from api.providers.iprovider import IProvider
from api.providers.providersnames import ProvidersNames
from api.languages import Languages
from api.utils import get_regex_results
from api.title import SeriesTitle
from api.title import MovieTitle


__all__ = ['Addic7edProvider']


class ADDIC7ED_PAGES:
    DOMAIN = 'www.addic7ed.com'
    SEARCH = 'http://%s/search.php?search=%s' % (DOMAIN, "%s")

class ADDIC7ED_REGEX:
    # Catches the results of the search result from the main page. For each
    # result, it returns: (TitleUrl, TitleName)
    SEARCH_RESULTS_PARSER = (
        '(?<=<td><a href=\")(?P<TitleUrl>.*?)(?:\" debug'
        '=\"\d+\">)(?P<TitleName>.*?)(?=</a>)'
    )
    # Catches the results when we query for something, and we're redirected to
    # a specific Title result (specific series episode, etc.). It seems that
    # this behavior (the redirection) only occur for episode, and not for movie
    # titles. The pattern returns: (TitleName, TitleUrl)
    REDIRECT_PAGE_PARSER = (
        '(?<=\<span class\=\"titulo\"\>)'
        '(?P<TitleName>.*?)(?: \<small\>Subtitle\<\/small\>.*?)'
        # Catches http://www.addic7ed.com
        '(?<=http\:\/\/www\.addic7ed\.com)'
        # Catches /serie/The_Big_Bang_Theory/3/4/The_Pirate_Solution
        '(?P<TitleUrl>\/serie\/[^\/]*\/\d*\/\d*\/[^\/]*?)'
        '(?=\" layout\=\"standard\")'
    )
    # Catches a version specific information from the title page. In this
    # context, a title means a specific episode or movie.
    # Returns:(VersionString, LanguageCode, DownloadUrl)
    RESULT_PAGE_PARSER = (
        '(?<=Version )(?P<VersionString>.*?)(?:, .*?javascript\:saveFavorite\\'
        '(\d+,)(?P<LanguageCode>\d+)(?:,\d+\).*?<a class=\"buttonDownload\"'
        ' href=\")(?P<DownloadUrl>.*?)(?=\">)'
    )


class Addic7edProvider(IProvider):
    """ The provider implementation for www.Addic7ed.com. """

    provider_name = ProvidersNames.ADDIC7ED
    # A mapping between the Language object and Addic7ed's own language code.
    language_to_addic7ed_code = {
        Languages.HEBREW    : 23,
        Languages.ENGLISH   : 1,
        Languages.SPANISH   : 4,
        Languages.ARABIC    : 38,
        Languages.BULGARIAN : 35,
        Languages.SLOVAK    : 25,
        Languages.TURKISH   : 16,
        Languages.CZECH     : 14,
        Languages.RUSSIAN   : 19,
        Languages.NORWEGIAN : 29,
        Languages.SWEDISH   : 18,
        Languages.FRENCH    : 8,
        Languages.GREEK     : 27
    }
    supported_languages = language_to_addic7ed_code.keys()

    def __init__(self, languages, requests_manager):
        super(Addic7edProvider, self).__init__(languages, requests_manager)



    def get_title_versions(self, title, version):
        logger.debug("Received call to get_title_version with %s,%s" %
            title, version)
        query_string = get_query_string(title)
        logger.debug("Using the query: %s" % query_string)
        search_url = format_query_url(query_string)

        search_content = self.requests_manager.perform_request(search_url)
        regex_results = get_regex_results(
            ADDIC7ED_REGEX.SEARCH_RESULTS_PARSER, search_content, True)

        # It means no redirection occurred.
        if regex_results:
            logger.debug(
                "The regex for the search page matched. "
                "No redirection occurred.")
        else:
            pass

def get_query_string(title):
    """
    Returns the query string for Addic7ed's. For movies it returns simply the
    name value, for series, it will return the name and the season_number and
    episode_number concatenated with 'x' between them (i.e, for episode 3 in
    season 10, it produces 10x3). If the episode name is specified and the
    episode numbering is missing, the name will be used instead.

    >>> from api.title import MovieTitle, SeriesTitle
    >>> print get_query_string(MovieTitle("The Matrix"))
    The Matrix
    >>> print get_query_string(SeriesTitle("The Big Bang Theory", 7, 12))
    The Big Bang Theory 7x12
    >>> print get_query_string(SeriesTitle("The Big Bang Theory", 7, 12, \
        "The Hesitation Ramification"))
    The Big Bang Theory 7x12
    >>> print get_query_string(SeriesTitle("The Big Bang Theory", \
        episode_name = "The Hesitation Ramification"))
    The Big Bang Theory The Hesitation Ramification
    """
    query = title.name
    if isinstance(title, SeriesTitle):
        query += " "
        if title.season_number:
            query += "%dx%d" % (title.season_number, title.episode_number)
        else:
            query += title.episode_name
    return query

def format_query_url(query):
    """
    Generates a well-formatted url string in order for it to be used as the
    search URL in Addic7ed.

    >>> print format_query_url("The Matrix")
    http://www.addic7ed.com/search.php?search=The%20Matrix
    >>> print format_query_url("Some Title With (Brackets)")
    http://www.addic7ed.com/search.php?search=Some%20Title%20With%20%28Brackets%29
    """
    from urllib2 import quote as url_quote
    return ADDIC7ED_PAGES.SEARCH % url_quote(query)

def extract_title_versions_from_title_page(page_content):
    pass
