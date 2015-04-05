import json
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger("subit.api.providers.subscenter.provider")

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages
from api.titlesversions import TitlesVersions


__all__ = ['SubscenterProvider']


class SUBSCENTER_PAGES:
    DOMAIN       = r'subscenter.cinemast.com'
    SEARCH       = r'http://{}/he/subtitle/search/?q={{query}}'.format(DOMAIN)
    MOVIE_JSON   = r'http://{}/he/cinemast/data/movie/sb/{{name}}/'.format(DOMAIN)
    EPISODE      = r'http://{}/he/subtitle/series/{{name}}/{{season}}/{{episode}}'.format(DOMAIN)
    EPISODE_JSON = r'http://{}/he/cinemast/data/series/sb/{{name}}/{{season}}/{{episode}}/'
    DOWNLOAD     = r'http://{}/subtitle/download/he/{{id}}/?v={{version_string}}&key={{key}}'.format(DOMAIN)

class SUBSCENTER_REGEX:
    pass    

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

    def _get_provider_versions_from_title_page(self, content):
        pass

    def get_title_versions(self, title, version):
        query_url = SUBSCENTER_PAGES.SEARCH.format(query=title.name)
        content = self.requests_manager.perform_request(query_url)

        if _is_title_page(content):
            provider_versions = \
                self._get_provider_versions_from_title_page(content)
            titles_versions = TitlesVersions(provider_versions)
        else:
            titles_urls = _get_titles_urls_from_search_results(content)
            import ipdb; ipdb.set_trace()

            titles_versions = TitlesVersions()
            for url in titles_urls:
                title_content = self.requests_manager.perform_request(url)
                provider_versions = \
                    self._get_provider_versions_from_title_page(title_content)
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