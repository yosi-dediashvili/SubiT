import logging
logger = logging.getLogger("subit.api.providers")

from api.exceptions import UnsupportedLanguage
from api.exceptions import InvalidProviderName

from api.requestsmanager import RequestsManager

__all__ = ['get_titles_versions']

# The list will contain the classes (not instances) of all the providers that
# SubiT knows of.
PROVIDERS = []


def get_provider_instance(provider_name, languages, 
    requests_manager_factory = RequestsManager.get_instance, 
    providers = PROVIDERS):
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


    