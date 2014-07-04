from abc import ABCMeta, abstractmethod, abstractproperty
class IProvider(object):
    __metaclass__ = ABCMeta

    supported_languages = []
    provider_name = None

    @abstractmethod
    def __init__(self, languages, requests_manager):
        pass

    @abstractmethod
    def get_title_versions(self, input):
        pass

    @abstractmethod
    def download_subtitle_buffer(self, provider_version):
        pass

    @abstractproperty
    def languages_in_use(self):
        pass