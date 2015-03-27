import logging
logger = logging.getLogger("subit.api.providers.torec.provider")
from bs4 import BeautifulSoup
import re

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.title import SeriesTitle, MovieTitle
from api.titles_versions import TitlesVersions
from api.languages import Languages
from api.utils import get_regex_match


__all__ = ['TorecProvider']


class TOREC_PAGES:
    DOMAIN   = r'www.torec.net'
    TICKET   = r'http://{}/ajax/sub/guest_time.asp'.format(DOMAIN)
    DOWNLOAD = r'http://{}/ajax/sub/downloadun.asp'.format(DOMAIN)
    SEARCH   = r'http://{}/ssearch.asp'.format(DOMAIN)
    SUBTITLE = r'http://{}/sub.asp'.format(DOMAIN)

class TOREC_REGEX:
    TITLE_NAME_IN_SEARCH = re.compile("(?<=\s\/\s)(.*?)(?=$)")

class TorecProvider(IProvider):
    provider_name = ProvidersNames.TOREC
    supported_languages = [
        Languages.HEBREW
    ]

    def __init__(self, languages, requests_manager):
        super(TorecProvider, self).__init__(languages, requests_manager)

    def get_title_versions(self, title, version):
        content = self.requests_manager.perform_request(
            TOREC_PAGES.SEARCH, {'search' : _get_query_string(title)})
        soup = BeautifulSoup(content)
        results_tables = soup.find_all(
            "table", style="margin:0 auto;width:600px;margin-right:0px;")
        for table in results_tables:
            link = table.find("a", style=None)
            name = get_regex_match(
                link.text, [TOREC_REGEX.TITLE_NAME_IN_SEARCH])
            sub_id = link.get("href")

            inner_table = table.find("table", style="width:440px;")
            if inner_table:
                spans = inner_table.find_all("span")
    
                def _is_year_str(string):
                    return get_regex_match(s.text.strip(), ["^\d{4}$"])

                def _is_versions_str(string):
                    return (
                        not _is_year_str(string) and 
                        all(
                            [get_regex_match(s.strip(), ["^[A-Za-z0-9]+$"]) 
                            for s in string.split(" / ")]))

                years = [s.text.strip() for s in spans 
                    if _is_year_str(s.text.strip())]
                year = int(years[0]) if years else 0

                versions = [s.text.strip() for s in spans 
                    if _is_versions_str(s.text.strip())]
                versions = versions[0].split(" / ") if versions else []
            else:
                year = 0
                versions = []

            

            


    def download_subtitle_buffer(self, provider_version):
        pass

def _get_query_string(title):
    """
    >>> m = MovieTitle("The Matrix", 1999, "tt0133093")
    >>> print _get_query_string(m)
    tt0133093
    >>> m = MovieTitle("The Matrix", 1999)
    >>> print _get_query_string(m)
    The Matrix
    >>> s = SeriesTitle("The Big Bang Theory", 2, 3)
    >>> print _get_query_string(s)
    The Big Bang Theory S02E03
    >>> s = SeriesTitle("The Big Bang Theory", episode_name = "The Holographic Excitation")
    >>> _get_query_string(s)
    Traceback (most recent call last):
        ...
    AssertionError: Can only search series with numbering.
    """
    if isinstance(title, MovieTitle):
        return _get_movie_query_string(title)
    else:
        return _get_series_query_string(title)
    
def _get_movie_query_string(movie_title):
    return movie_title.imdb_id or movie_title.name

def _get_series_query_string(series_title):
    assert series_title.got_numbering, "Can only search series with numbering."
    return ("{0.name} S{0.season_number:02d}E{0.episode_number:02d}"
        .format(series_title))
