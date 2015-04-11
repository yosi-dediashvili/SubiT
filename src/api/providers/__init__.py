import logging
logger = logging.getLogger("subit.api.providers")

from api.exceptions import UnsupportedLanguage
from api.exceptions import InvalidProviderName
from api.requestsmanager import get_manager_instance
from api.providers.providersnames import ProvidersNames


__all__ = ['get_titles_versions', 'ProvidersNames']

# The list will contain the classes (not instances) of all the providers that
# SubiT knows of.
def _get_all_providers():
    from api.providers.opensubtitles import OpenSubtitlesProvider
    from api.providers.addic7ed import Addic7edProvider
    from api.providers.torec import TorecProvider
    from api.providers.subscenter import SubscenterProvider
    return [
        OpenSubtitlesProvider, 
        Addic7edProvider, 
        TorecProvider, 
        SubscenterProvider
    ]

def get_provider_instance(provider_name, languages, 
    requests_manager_factory = get_manager_instance, 
    providers = None):
    """
    Factory method for creating Provider instances. The provider_name value 
    should be a valid ProviderName instance. If none of the providers specified
    in the providers list does not match the ProviderName, InvalidProviderName
    exception is raised. languages should be a list of one or more Language 
    instances from the Languages class.

    A RequestsManager factory method can be passed to the function in order to 
    bypass the default factory method. Also, a list of Provider classes can be
    passed to the factory in order to override the list it looks in in order
    to find the matching provider.

    If none of the languages specified is supported in the provider specified,
    an UnsupportedLanguage exception will be raised.
    """
    logger.debug("get_provider_instance called with: %s, %s" 
        % (provider_name, languages))

    providers = providers or _get_all_providers()
    available_providers = {p.provider_name: p for p in providers}
    if provider_name not in available_providers:
        logger.error("Only available provider names are: %s" 
            % available_providers.keys())
        raise InvalidProviderName(
            "No such provider_name was located in the providers: %s" 
            % provider_name)

    provider_class = available_providers[provider_name]
    logger.debug("Found the provider: %s" % provider_class)
    
    available_languages = list(
        set(languages).intersection(set(provider_class.supported_languages)))
    logger.debug("available_languages: %s" % available_languages)
    if not available_languages:
        logger.error("Not a single language is available in that provider.")
        raise UnsupportedLanguage(
            "The provider does not support any required language.")

    requests_manager = requests_manager_factory(provider_name.full_name)
    logger.debug("Received a RequestsManager: %s" % requests_manager)
    provider = provider_class(languages, requests_manager)
    logger.debug("Created a provider instance: %s" % provider)
    return provider