import logging
logger = logging.getLogger("subit.api.providers.torec.provider")
from bs4 import BeautifulSoup
import re
from collections import namedtuple

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.title import SeriesTitle, MovieTitle
from api.version import ProviderVersion
from api.titlesversions import TitlesVersions
from api.languages import Languages
from api.utils import get_regex_match, get_regex_results
from api.exceptions import HTMLParsingError


__all__ = ['TorecProvider']


class TOREC_PAGES:
    DOMAIN   = r'www.torec.net'
    TICKET   = r'http://{}/ajax/sub/guest_time.asp'.format(DOMAIN)
    DOWNLOAD = r'http://{}/ajax/sub/downloadun.asp'.format(DOMAIN)
    SEARCH   = r'http://{}/ssearch.asp'.format(DOMAIN)
    SUB_PAGE = r'http://{0}/sub.asp?sub_id={{0}}'.format(DOMAIN)

class TOREC_REGEX:
    TITLE_NAME_IN_SEARCH = re.compile("(?<=\s\/\s)(.*?)(?=$)")
    TITLE_NAME_TO_EPISODE = re.compile("(.*?) \- Season (\d+) Episode (\d+)")

class TorecProvider(IProvider):
    provider_name = ProvidersNames.TOREC
    supported_languages = [
        Languages.HEBREW
    ]

    def __init__(self, languages, requests_manager):
        super(TorecProvider, self).__init__(languages, requests_manager)
        from api.providers.torec.hamster import TorecHashCodesHamster
        self._hamster = TorecHashCodesHamster(self.requests_manager)

    def _get_provider_versions_for_subid(self, sub_id):
        from api.identifiersextractor import extract_identifiers

        sub_page = self.requests_manager.perform_request(
            TOREC_PAGES.SUB_PAGE.format(sub_id))

        soup = BeautifulSoup(sub_page)
        title = _get_title_from_sub_page(soup)

        provider_versions = []
        for version_string, version_code in \
            _get_versions_strings_and_versions_ids_from_sub_page(soup):

            identifiers = extract_identifiers(title, [version_string])
            provider_version = ProviderVersion(
                identifiers, 
                title, 
                self.languages_in_use[0], # We only support one language
                self, 
                version_string, 
                {"version_code" : version_code, "sub_id" : sub_id})

            provider_versions.append(provider_version)

        return provider_versions

    def get_title_versions(self, title, version):
        content = self.requests_manager.perform_request(
            TOREC_PAGES.SEARCH, {'search' : _get_query_string(title)})
        soup = BeautifulSoup(content)

        tables_headers = soup.find_all(
            lambda tag: tag.name == "td" and 
                        "newd_table_titleLeft_BG" in tag.get("class",[]) and 
                        tag.find("a"))

        sub_ids = _get_subids_from_tables_headers(tables_headers)
        titles_versions = TitlesVersions()
        for sub_id in sub_ids:
            self._hamster.add_sub_id(sub_id)
            versions = self._get_provider_versions_for_subid(sub_id)
            for version in versions:
                titles_versions.add_version(version)

        return titles_versions

    def download_subtitle_buffer(self, provider_version):
        sub_id       = provider_version.attributes['sub_id']
        version_code = provider_version.attributes['version_code']
        
        # The fake subtitle file is inside a zip file. The size of the zip file
        # is ~3KB. We set  our limit to 4KB just in case...
        fake_file_size_limit = 4096
        max_fake_downloads = 5

        def _try_download():
            fake_downloads_count = 0
            headers_to_add = {
                'Cookie'  : 'Torec%5FNC%5Fs=1600;',
                'Referer' : TOREC_PAGES.SUB_PAGE.format(sub_id)
            }
            # Run until we reach maximum fake downloads
            while fake_downloads_count < max_fake_downloads:
                logger.debug("Trying to download: {}/{}".format(
                    fake_downloads_count, max_fake_downloads))
                sub_url = None
                # Until we get a legit sub_url value.
                while not sub_url:
                    ticket = self._hamster.get_ticket(sub_id)
                    post_data = _get_download_post_data(ticket, version_code)
                    # Retrieve the result (the url to the subtitle)
                    sub_url = self.requests_manager.perform_request(
                        TOREC_PAGES.DOWNLOAD,
                        data = post_data,
                        more_headers = headers_to_add)

                    if not sub_url.startswith("/ajax/sub/sdls.asp"):
                        logger.debug("Got bad url: {!r}".format(sub_url))
                        sub_url = None
                        continue

                    file_name, content = self.requests_manager.download_file(
                        "http://{}/{}".format(
                            TOREC_PAGES.DOMAIN, sub_url.lstrip("/")),
                        more_headers = headers_to_add)
                    file_size = len(content)
                    # If it's not the fake one.
                    if file_size > fake_file_size_limit:
                        logger.debug('Received real subtitle from Torec!')
                        self._hamster.remove_sub_id(sub_id)
                        return (file_name, content)
                    # If it's a fake, increase the counter.
                    else:
                        logger.debug('Received fake subtitle from Torec!')
                        fake_downloads_count = fake_downloads_count + 1
            return (None, None)

        file_name, content = _try_download()
        if not (file_name and content):
            logger.error("Failed downloading subtitle from Torec.")
        else:
            logger.debug("Downloaded file: {}".format(file_name))
        return (file_name, content)


def _get_versions_strings_and_versions_ids_from_sub_page(sub_page_soup):
    def _is_version_option(tag):
        return (tag.name == "option" and 
                tag.parent.get("id") == "download_version")
    def _is_version_string_tag(tag):
        return (tag.name == "span" and  
                not tag.get("style") and
                tag.parent.name == "p" and 
                tag.parent.get("id") == "version_list")

    versions_ids = [tag.get("value") 
        for tag in sub_page_soup.find_all(_is_version_option)]
    versions_strings = [tag.text 
        for tag in sub_page_soup.find_all(_is_version_string_tag)]
    
    assert len(versions_ids) == len(versions_strings), (
        "Size mismatch between the versions strings and ids: {}!={}"
        .format(len(versions_strings), len(versions_ids)))

    return zip(versions_strings, versions_ids)

def _get_title_from_sub_page(sub_page_soup):
    name = sub_page_soup.find("bdo").text    
    imdb_link = sub_page_soup.find("a", id="sub_imdb_link").get("href")
    imdb_id = get_regex_match(imdb_link, "tt\d+")

    if _is_episode_sub_page(sub_page_soup):
        name, season, episode = _get_episode_params_from_name(name)
        return SeriesTitle(name, int(season), int(episode), imdb_id=imdb_id)
    else:
        return MovieTitle(name, imdb_id=imdb_id)

def _is_episode_sub_page(sub_page_soup):
    return sub_page_soup.find("img", src="/images/tv_series_button.gif")

def _get_episode_params_from_name(name):
    """
    >>> name = "The Big Bang Theory - Season 8 Episode 13"
    >>> print _get_episode_params_from_name(name)
    ('The Big Bang Theory', '8', '13')
    >>> name = "The Big Bang Theory"
    >>> _get_episode_params_from_name(name)
    Traceback (most recent call last):
        ...
    HTMLParsingError: name does not look like an episode: \
    'The Big Bang Theory': ...
    """
    try:
        error = None
        result = tuple(
            get_regex_results(name, TOREC_REGEX.TITLE_NAME_TO_EPISODE))
    except Exception as ex:
        error = ex
    finally:
        if not result:
            raise HTMLParsingError(
                "name does not look like an episode: {!r}: {!r}"
                .format(name, error))
        return result[0]

def _get_subids_from_tables_headers(table_headers):
    def _extract(header):
        link = header.find("a")
        sub_uri = link.get("href")
        return int(get_regex_match(sub_uri, "/sub\.asp\?sub_id\=(\d+)"))

    return map(_extract, table_headers)

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

def _get_download_post_data(ticket, version_code):
    """ Function to build well-formatted get request for subtitle. """
    return {
        # sub_id, same for all sub versions
        'sub_id'        : ticket.sub_id,       
        # Are we guests (Not logged in)?
        'sh'            : 'yes',        
        'guest'         : ticket.guest_code,   
        'timewaited'    : ticket.time_past,  
        # Code for the specific version
        'code'          : version_code
    }
