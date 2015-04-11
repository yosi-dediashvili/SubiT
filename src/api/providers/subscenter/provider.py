import json
from bs4 import BeautifulSoup
import re
import logging
logger = logging.getLogger("subit.api.providers.subscenter.provider")

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages
from api.titlesversions import TitlesVersions
from api.utils import get_regex_match
from api.title import MovieTitle, SeriesTitle

__all__ = ['SubscenterProvider']


class SUBSCENTER_PAGES:
    DOMAIN       = r'subscenter.cinemast.com'
    SEARCH       = r'http://{}/he/subtitle/search/?q={{query}}'.format(DOMAIN)
    MOVIE_JSON   = r'http://{}/he/cinemast/data/movie/sb/{{movie_id}}/'.format(DOMAIN)
    EPISODE      = r'http://{}/he/subtitle/series/{{name}}/{{season}}/{{episode}}'.format(DOMAIN)
    EPISODE_JSON = r'http://{}/he/cinemast/data/series/sb/{{movie_id}}/{{season}}/{{episode}}/'.format(DOMAIN)
    DOWNLOAD     = r'http://{}/subtitle/download/he/{{id}}/?v={{version_string}}&key={{key}}'.format(DOMAIN)

class SUBSCENTER_REGEX:
    EPISODES_JSON_FROM_SCRIPT = re.compile("(?<=var episodes_group \= ).*?}}}")
    MOVIE_ID = re.compile("(?<=var movie_id \= \').*?(?=\';)")

class SubscenterProvider(IProvider):
    provider_name = ProvidersNames.SUBSCENTER
    supported_languages = [
        Languages.HEBREW
    ]

    def __init__(self, languages, requests_manager):
        super(SubscenterProvider, self).__init__(languages, requests_manager)
  
    def _request_json(self, url):
        content = self.requests_manager.perform_request(url)
        return json.loads(content)

    def _get_provider_versions_from_title_page(self, content, queried_title):
        soup = BeautifulSoup(content)
        title = _get_title_from_title_page(soup, queried_title)
        json_url = _get_json_url_from_title_page(soup, title)

    def get_title_versions(self, title, version):
        query_url = SUBSCENTER_PAGES.SEARCH.format(query=title.name)
        content = self.requests_manager.perform_request(query_url)

        if _is_title_page(content):
            provider_versions = \
                self._get_provider_versions_from_title_page(content, title)
            titles_versions = TitlesVersions(provider_versions)
        else:
            titles_urls = _get_titles_urls_from_search_results(content)
            titles_versions = TitlesVersions()
            for url in titles_urls:
                title_content = self.requests_manager.perform_request(url)
                provider_versions = \
                    self._get_provider_versions_from_title_page(
                        title_content, title)
                for ver in provider_versions:
                    titles_versions.add_version(ver)

        return titles_versions

    def download_subtitle_buffer(self, provider_version):
        pass

def _is_title_page(content):
    return "http://www.imdb.com" in content

def _get_titles_urls_from_search_results(content):
    soup = BeautifulSoup(content)
    divs = soup.find_all("div", class_="generalWindow process movieProcess")
    return [div.find("a").get("href") for div in divs]

def _get_json_from_series_page(soup):
    json_script = soup.find(
        lambda tag: tag.name == "script" and "episodes_group" in tag.text)
    json_content = get_regex_match(
        json_script.text, SUBSCENTER_REGEX.EPISODES_JSON_FROM_SCRIPT)
    return json.loads(json_content)

def _get_any_title_params_from_title_page(soup):
    name = soup.find("h3").text
    year = int(soup.find(
        lambda tag: tag.name == "strong" and tag.text.isdigit()).text)
    imdb_url = soup.find(
        lambda tag: tag.name == "a" and 
                    "imdb" in tag.get("href", "")).get("href")
    imdb_id = imdb_url.split("/")[-2]
    if not imdb_id.startswith("tt"):
        logger.debug("Failed extracting imdb_id from title page. Got url: {}"
            .format(imdb_url))
        imdb_id = ""
    return (name, year, imdb_id)

def _get_series_title_from_title_page(soup, queried_title):
    name, year, imdb_id = _get_any_title_params_from_title_page(soup)
    episodes_json = _get_json_from_series_page(soup)
    for season in episodes_json.itervalues():
        for episode in season.itervalues():
            if (int(episode['season_id']) == queried_title.season_number and 
                int(episode['episode_id']) == queried_title.episode_number):
                
                return SeriesTitle(name, 
                    queried_title.season_number, queried_title.episode_number)
    return None

def _get_title_from_title_page(soup, queried_title):
    if 'episodes_group' in soup.text:
        return _get_series_title_from_title_page(soup, queried_title)
    else:
        return MovieTitle(*_get_any_title_params_from_title_page(soup))

def _get_json_url_from_title_page(soup, extracted_title):
    movie_id_script = soup.find(
        lambda tag: tag.name == "script" and "movie_id" in tag.text).text
    movie_id = get_regex_match(movie_id_script, SUBSCENTER_REGEX.MOVIE_ID)
    if isinstance(extracted_title, MovieTitle):
        return SUBSCENTER_PAGES.MOVIE_JSON.format(movie_id=movie_id)
    else:
        return SUBSCENTER_PAGES.EPISODE_JSON.format(
            movie_id=movie_id, 
            season=extracted_title.season_number, 
            episode=extracted_title.episode_number)
