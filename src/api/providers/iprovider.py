from abc import ABCMeta, abstractmethod, abstractproperty
class IProvider(object):
    __metaclass__ = ABCMeta

    supported_languages = []
    provider_name = None

    @abstractmethod
    def __init__(self, languages, requests_manager):
        self.languages = languages
        self._languages_in_use = list(
            set(type(self).supported_languages).intersection((set(languages))))
        self.requests_manager = requests_manager

    @abstractmethod
    def get_title_versions(self, title, version):
        pass

    @abstractmethod
    def download_subtitle_buffer(self, provider_version):
        pass

    def languages_in_use(self):
        return self._languages_in_use
