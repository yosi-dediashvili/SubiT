import logging
logger = logging.getLogger("subit.api.providers.torec.provider")

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages


__all__ = ['TorecProvider']


class TOREC_PAGES:
    DOMAIN   = r'www.torec.net'
    TICKET   = r'http://{}/ajax/sub/guest_time.asp'.format(DOMAIN)
    DOWNLOAD = r'http://{}/ajax/sub/downloadun.asp'.format(DOMAIN)
    SEARCH   = r'http://{}/ssearch.asp'.format(DOMAIN)
    SUBTITLE = r'http://{}/sub.asp'.format(DOMAIN)

class TorecProvider(IProvider):
    provider_name = ProvidersNames.TOREC
    supported_languages = [
        Languages.HEBREW
    ]

    def __init__(self, languages, requests_manager):
        super(TorecProvider, self).__init__(languages, requests_manager)

    def get_title_versions(self, title, version):
        pass

    def download_subtitle_buffer(self, provider_version):
        pass