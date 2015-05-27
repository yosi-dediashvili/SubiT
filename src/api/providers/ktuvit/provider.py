import logging
logger = logging.getLogger("subit.api.providers.ktuvit.provider")

from bs4 import BeautifulSoup
import re

from api.providers.iprovider import IProvider
from api.providers.providersnames import ProvidersNames
from api.title import MovieTitle, SeriesTitle
from api.languages import Languages
from api.utils import get_regex_match
from api.titlesversions import TitlesVersions
from api.identifiersextractor import extract_identifiers


__all__ = ['KtuvitProvider']


class KtuvitException(Exception): pass
class MissingSeasonException(KtuvitException): pass
class MissingEpisodeException(KtuvitException): pass

class KTUVIT_PAGES:
    DOMAIN = "www.ktuvit.com"
    QUERY = "http://{}/browse.php?q={{}}".format(DOMAIN)
    SERIES_PAGE = "http://{}/viewseries.php?id={{}}".format(DOMAIN)
    SEASON_PAGE = "http://{}/getajax.php?seasonid={{}}".format(DOMAIN)
    EPISODE_PAGE = "http://{}/getajax.php?episodedetails={{}}".format(DOMAIN)


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
        if my_tag:
            return my_tag.get("id").split("_")[-1]
        else:
            return None

    def _get_episode_id_from_series_soup(self, series_soup, season, episode):
        season_str = str(season)
        episode_str = str(episode)
        
        season_id = self._get_id(series_soup, "seasonlink", season_str)
        if not season_id:
            raise MissingSeasonException()
        season_url = KTUVIT_PAGES.SEASON_PAGE.format(season_id)
        logger.debug("Using season_url: {}".format(season_url))

        season_content = self.requests_manager.perform_request(season_url)
        season_soup = BeautifulSoup(season_content)
        episode_id = self._get_id(season_soup, "episodelink", episode_str)
        if not season_id:
            raise MissingEpisodeException()
        logger.debug("Got episode_id: {}".format(episode_id))
        return episode_id

    def _get_providers_versions_from_episode_page(
        self, extracted_title, episode_soup):

        tds = episode_soup.find_all("td", class_="subtitle_tab")
        providers_versions = []
        for td in tds:
            # The <a> right after it is the version id.
            version_id = td.find("a").get("name")
            lang_div = td.find("div", class_="subt_lang")
            # The hebrew lang.
            if lang_div.find("img").get("src") != 'images/Flags/1.png':
                continue
            version = td.find("div", class_="subtitle_title").get("title")
            identifiers = extract_identifiers(extracted_title, version)
            provider_version = ProviderVersion(
                identifiers, 
                extracted_title, 
                Languages.HEBREW,
                self,
                version,
                attributes={"version_id" : version_id})
            providers_versions.append(provider_version)

        return providers_versions

    def _extract_series_title(self, queried_title, series_soup, episode_soup):
        """ We assume the episode numbering to be the same as the query. """
        series_name, series_first_year, series_imdb_id = \
            extract_title_params(series_soup)

        episode_year_link = episode_soup.find(
            lambda tag: tag.name == "a" and "uy=" in tag.get("href"))
        episode_year = int(episode_year_link.get_text())

        episode_name_tag = episode_soup.find(
            "span", class_="smtext", style="direction:ltr;text-align:right;")
        episode_name = episode_name_tag.get_text() if episode_name_tag else ""

        epiosde_imdb_link = episode_soup.find(
            lambda tag: tag.name == "a" and "imdb" in tag.get("href", ""))
        episode_imdb_url = epiosde_imdb_link.get("href", "") \
            if epiosde_imdb_link else ""
        episode_imdb_id = episode_imdb_url.split("/")[-1]

        return SeriesTitle(series_name, 
            queried_title.season_number, 
            queried_title.episode_number, 
            episode_imdb_id, 
            episode_name, 
            episode_year, 
            series_imdb_id)

    def _extract_movie_title(self, soup):
        return MovieTitle(*extract_title_params(soup))

    def _get_titles_versions_for_episode(self, title, titles_ids):        
        titles_versions = TitlesVersions()
        # We assume that we get only the titles with is_series set to True.
        for is_series, title_id in titles_ids:
            series_page = self.requests_manager.perform_request(
                KTUVIT_PAGES.SERIES_PAGE.format(title_id))
            series_soup = BeautifulSoup(series_page)

            try:
                episode_id = self._get_episode_id_from_series_soup(
                    series_soup, title.season_number, title.episode_number)
            except KtuvitException as ex:
                logger.debug("Failed getting episode_id from title_id: {}, {}"
                    .format(title_id, ex))
                continue

            episode_page = self.requests_manager.perform_request(
                KTUVIT_PAGES.EPISODE_PAGE.format(episode_id))
            episode_soup = BeautifulSoup(episode_page)
            series_title = self._extract_series_title(
                title, series_soup, episode_soup)
            import ipdb; ipdb.set_trace()
            if not series_title:
                logger.debug("Failed getting series title for title_id: {}"
                    .format(title_id))
                continue

            providers_versions = self._get_providers_versions_from_episode_page(
                series_title, episode_soup)
            if providers_versions:
                for provider_version in providers_versions:
                    titles_versions.add_version(provider_version)
        return titles_versions

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
                filter(lambda title_id: title_id[0], titles_ids))
        else:
            return self._get_titles_versions_for_movie(title, 
                filter(lambda title_id: not title_id[0], titles_ids))

    def download_subtitle_buffer(self, provider_version):
        pass


def extract_title_params(soup):
    """ Returns a tuple of the title's name, year and imdb_id. """

    def is_title_div(tag):
        return (
            tag.name == "div" and 
            tag.get("class", "missing")[0] == "g-res-title-prop-rtl" and 
            tag.next.name == "span" and 
            tag.next.get("class", "missing")[0] == "Gray")
    div = soup.find(is_title_div)

    name = list(div.stripped_strings)[1]
    year_links = soup.find_all(
        lambda tag: tag.name == "a" and "uy=" in tag.get("href"))
    # The third link contains the year for the title.
    year = int(year_links[2].get_text())
    imdb_link = soup.find(
        lambda tag: tag.name == "a" and "imdb" in tag.get("href"))\
        .get("href")
    imdb_id = imdb_link.split("/")[-1]
    return (name, year, imdb_id)

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
    [(False, '1147'), (False, '1645'), (False, '1656'), (False, '1688'), (False, '1974')]
    >>> content = requests.get("http://www.ktuvit.com/browse.php?q=Alias").content
    >>> ids = get_titles_ids_from_query_content(content)
    >>> print(sorted(ids))
    [(False, '122609'), (True, '266')]
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
    