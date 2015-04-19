import logging
logger = logging.getLogger("subit.api.providers.ktuvit.provider")

from bs4 import BeautifulSoup
import re

from api.providers.iprovider import IProvider
from api.providers.providersnames import ProvidersNames
from api.title import MovieTitle, SeriesTitle
from api.languages import Languages
from api.utils import get_regex_match


__all__ = ['KtuvitProvider']


class KTUVIT_PAGES:
    DOMAIN = "www.ktuvit.com"
    QUERY = "http://{}/browse.php?q={{}}".format(DOMAIN)
    SERIES_PAGE = "http://{}/viewseries.php?id={{}}".format(DOMAIN)
    SEASON_PAGE = "http://{}/getajax.php?seasonid={{}}".format(DOMAIN)


class KTUVIT_REGEX:
    URI_TO_TITILE_ID = re.compile("(?<=id\=)\d+")

class KtuvitProvider(IProvider):
    provider_name = ProvidersNames.KTUVIT
    supported_languages = [Languages.HEBREW]

    def __init__(self, languages, requests_manager):
        super(KtuvitProvider, self).__init__(languages, requests_manager)


    def _get_id(self, soup, link_id, my_expected_id):
        def is_my_id(tag):
            return (
                tag.name == "a" and 
                link_id in tag.get("id", "") and 
                tag.get_text() == my_expected_id)

        my_tag = soup.find(is_my_id)
        return my_tag.split("_")[-1]


    def _get_episode_id_from_series_soup(self, series_soup, season, episode):
        season_str = str(season)
        episode_str = str(episode)
        
        season_id = self._get_id(series_soup, "seasonlink", season_str)
        season_url = KTUVIT_PAGES.SEASON_PAGE.format(season_id)
        logger.debug("Using season_url: {}".format(season_url))

        season_content = self.requests_manager.perform_request(season_url)
        season_soup = BeautifulSoup(season_content)
        episode_id = self._get_id(season_soup, "episodelink", episode_str)
        logger.debug("Got episode_id: {}".format(episode_id))
        return episode_id

    def _get_providers_versions_from_content(self, extracted_title, content):
        pass

    def _extract_movie_title(self, soup):
        td = soup.find("td", 
            style="direction:ltr;text-align:right;padding-right:8px;"
                "padding-bottom:1px;padding-top:1px;")
        name = td.stripped_strings[1]
        year_link = soup.find(
            lambda tag: tag.name == "a" and "uy=" in tag.get("href"))
        year = int(year_link.get_text())
        imdb_link = soup.find(
            lambda tag: tag.name == "a" and "imdb" in tag.get("href"))\
            .get("href")
        imdb_id = imdb_link.split("/")[-1]
        return MovieTitle(name, year, imdb_id)

    def _extract_episode_title(self, series_soup, episode_soup):
        pass

    def _get_titles_versions_for_episode(self, title, titles_ids):
        for is_series, title_id in titles_ids:


    def _get_titles_versions_for_movie(self, title, titles_ids):
        pass


    def get_title_versions(self, title, version):
        logger.debug("get_title_versions got called with: {}, {}"
            .format(title, version))
        
        query_string = get_query_string(title)
        query_url = KTUVIT_PAGES.QUERY.format(query_string)
        query_content = self.requests_manager.perform_request(query_url)

        titles_ids = get_titles_ids_from_query_content(query_content)
        logger.debug("Got titles_ids: {}".format(titles_ids))
        if isinstance(title, SeriesTitle):
            return self._get_titles_versions_for_episode(title, 
                filter(lambda is_series, title_id: is_series, titles_ids))
        else:
            return self._get_titles_versions_for_movie(title, 
                filter(lambda is_series, title_id: is_series, titles_ids))






def get_query_string(title):
    """
    >>> title = MovieTitle("The Matrix", 1999, "tt0133093")
    >>> print(get_query_string(title))
    tt0133093
    >>> title = MovieTitle("The Matrix", 1999)
    >>> print(get_query_string(title))
    The+Matrix
    """
    return title.imdb_id or title.name.replace(" ", "+")

def get_titles_ids_from_query_content(query_content):
    """
    >>> import requests
    >>> content = requests.get("http://www.ktuvit.com/browse.php?q=The+Matrix").content
    >>> ids = get_titles_ids_from_query_content(content)
    >>> print(sorted(ids))
    [(False, u'1147'), (False, u'1645'), (False, u'1656'), (False, u'1688'), (False, u'1974')]
    >>> content = requests.get("http://www.ktuvit.com/browse.php?q=Alias").content
    >>> ids = get_titles_ids_from_query_content(content)
    >>> print(sorted(ids))
    [(False, u'122609'), (True, u'266')]
    """
    soup = BeautifulSoup(query_content)
    urls = soup.find_all("a", itemprop="url")

    title_ids = []
    for url in urls:
        href = url.get("href")
        title_id = get_regex_match(href, KTUVIT_REGEX.URI_TO_TITILE_ID)
        is_series = 'viewseries' in href
        title_ids.append((is_series, title_id))
    return title_ids
    