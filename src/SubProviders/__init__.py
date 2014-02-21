import inspect
import os
import sys

from Utils import GetProgramDir
from Utils import myfilter
from Utils import WriteDebug

from Queue import Queue
from itertools import groupby

import SubiT

from Settings.Config import SubiTConfig

#============================================================================= #
# We need to import all the providers so that the cx_freeze will know that he 
# needs to include the providers dependencies also
from SubProviders.ISubProvider import ISubProvider
from SubProviders import Subtitle
from SubProviders import SubsCenter
from SubProviders import Torec
from SubProviders import OpenSubtitles
from SubProviders import Addic7ed
from SubProviders import Subscene
#============================================================================= #

SUBPROVIDERS_DIR_LOCATION = os.path.join(GetProgramDir(), 'SubProviders')

# Will stores the provider's modules (The ones return from __import__) and 
# not the providers itself
TotalProviderModules = []

# Will store all the providers avaliable in the SubProviders directory 
# (contains also the providers that got filtered out by the configuration).
AllAvaliableProviders  = []

# Stores the providers in the right order, according to the configuration
RelevantProvidersOrdered = Queue(100)

# Stores the current SubProvider
CurrentSubProvider = None


def storeISubProviderImplementations(startModule):
    """ This functions gets a loaded module as input, and stores all the 
        ISubProvider implementation under it.  The function uses the inspect 
        module functions in order to do most of the work. If the object is 
        module, we call ourself again, with the object as parameter. If the 
        object is class, it will be stored in the AllAvaliableProviders list 
        if:
            1. Is a SubClass of ISubProvider
            2. Is not ISubProvider itself
            3. His PROVIDER_NAME value doesn't starts in "Base - "
        On any failure, we proceed to the next module.
    """

    # The directory in which the module file (py) seats
    start_module_path = os.path.split(inspect.getabsfile(startModule))[0]
    # Lambda to check if the current object is placed under the start module
    _isUnderPathOfStartModule = lambda current: \
        start_module_path in os.path.split(inspect.getabsfile(current))[0]
    # inspect.getmembers gives us a (key, value) tuple for each object
    for name, obj in inspect.getmembers(startModule):
        try:
            # In order to avoid checking python infrastracture modules, we 
            # check if the current module is located under the start module 
            # directory.
            if inspect.ismodule(obj) and _isUnderPathOfStartModule(obj):
                storeISubProviderImplementations(obj)
            elif inspect.isclass(obj):
                if issubclass(obj, ISubProvider) and obj is not ISubProvider:
                    if ('Base - ' not in obj.PROVIDER_NAME and 
                        obj not in AllAvaliableProviders):
                        AllAvaliableProviders.append(obj)
        except Exception as eX: 
            WriteDebug( 'Provider load Failure => %s' % eX )

def getSubProviders():
    """ Function to retrieve all avaliable providers (not just the ones that
        configured in the configuration). Use getNextProvider() in order to get 
        providers from the queue.
    """
    return AllAvaliableProviders

def getSubProviderPngByName(provider_name):
    """ Function to get the PROVIDER_PNG of a provider, the provider_name can 
        be either a real name, i.e. a value from PROVIDER_NAME, or just the 
        provider url (without the language part). On failure, the function 
        return the icon-subprovider-unknown.png string.
    """
    provider_png = 'icon-subprovider-unknown.png'
    provider = getSubProviderByName(provider_name)
    
    WriteDebug('Trying to get the png of: %s' % provider_name)
    if not provider:
        WriteDebug('Couldnt get the provider using it name')
        provider_languages = getAvaliableLanguages(provider_name)
        if provider_languages:
            WriteDebug('Got provider languages')
            provider_lang = provider_languages[0]
            WriteDebug('First language of the provider is: %s' % provider_lang)
            provider_name = buildSubProviderName(provider_lang, provider_name)
            provider = getSubProviderByName(provider_name)

    if provider:
        WriteDebug('Got a real provider by the name')
        provider_png = provider.PROVIDER_PNG
    else:
        WriteDebug('Couldnt get the provider after all, returning the default png')

    return provider_png

def getSubProviderByName(provider_name):
    """ Function to get an provider using PROVIDER_NAME value. On failure, 
        returns None.
    """
    provider = None
    WriteDebug('Trying to get provider: %s' % provider_name)
    try:
        provider = myfilter\
            (lambda provider: provider.PROVIDER_NAME == provider_name, 
             getSubProviders(), take_first = True)
        if provider:
            WriteDebug('Found match for provider name: %s' % provider_name)
        else:
            WriteDebug('No such provider: %s' % provider_name)
    except Exception as eX:
        WriteDebug('Failed getting provider: %s -> %s' % (provider_name, eX))
    return provider

def getSelectedLanguages():
    """ Function to get the selected languages currently set for SubiT. """
    return SubiTConfig.Singleton().getList('Providers', 'languages_order')

def getSelectedProviders():
    """ Function to get the selected providers currently set for SubiT. """
    return SubiTConfig.Singleton().getList('Providers', 'providers_order')

def getAvaliableLanguages(provider = None):
    """ Function to get all the avaliable languages under the current list of 
        SubProviders. If provider is given, the result will be all the langs 
        under the given provider.
    """
    all_languages   = []
    for provider_name in map(lambda x: x.PROVIDER_NAME, getSubProviders()):
        # If provider is not None, and the provider is not in provider_name
        if not provider or provider in provider_name:
            provider_lang = provider_name.split(' - ')[0]
            if provider_lang != 'Global' and not provider_lang in all_languages:
                all_languages.append(provider_lang)
    # We return asc order of the languages
    return sorted(all_languages)

def getAvaliableSubProviders(language = None):
    """ Function to get all the avaliable providers names under the current 
        SubProviders list. If language is given, the result will be all the 
        providers that supports the given langauge. The elements are the 
        PROVIDER_NAME values.
    """
    all_providers = []
    for provider_name in map(lambda x: x.PROVIDER_NAME, getSubProviders()):
        # If language is not None, and the language is not in provider_name
        if not language or language in provider_name:
            provider_name = provider_name.split(' - ')[1]
            if not provider_name in all_providers:
                all_providers.append(provider_name)
    # We return asc order of PROVIDER_NAME
    return sorted(all_providers) 


def getNextSubProvider():
    """ Function to get the next provider in the queue. """
    nextProvider = RelevantProvidersOrdered.get_nowait()
    WriteDebug('Giving next provider: %s' % nextProvider.PROVIDER_NAME)
    return nextProvider


def getSubProvider(iSubProvider = None):
    """ Return the currently set provider. """
    # If there's not current provider, and we didn't pass iSubProvider instance
    global CurrentSubProvider
    if not CurrentSubProvider and not iSubProvider:
        raise Exception('No SubProvider Passed!')
    elif iSubProvider:
        WriteDebug('Setting provider: %s' % iSubProvider.PROVIDER_NAME)
        # Set the provider
        CurrentSubProvider = iSubProvider
        CurrentSubProvider()
    return CurrentSubProvider

def setNextSubProvider():
    """ This function will set the next provider in line to be our current 
        provider.
    """
    try:
        getSubProvider(getNextSubProvider())()
        return True
    except:
        return False

def buildSubProviderName(lang, name):
    """ Build the PROVIDER_NAME using the lang and name values. 
        result is "lang - name", ie: Hebrew - www.torec.net.
    """
    return '%s - %s' % (lang, name)

def getLanguageFromProviderName(name):
    """ Will return the first part of the provider name - the language. """
    return name.split(' - ')[0]

def getNameFromProviderName(name):
    """ Will return the second part of the provider name - the name. """
    return name.split(' - ')[1]

#===========================================================
# First, import all the modules under SubProviders directory.
#===========================================================
sys.path.append(__path__[0])
WriteDebug('SubProviders Current Path is: %s' % SUBPROVIDERS_DIR_LOCATION)
for module in os.listdir(SUBPROVIDERS_DIR_LOCATION):
    fullpathModule = os.path.join(SUBPROVIDERS_DIR_LOCATION, module)
    # dir means: this is a module
    if os.path.isdir(fullpathModule):
        try:
            TotalProviderModules.append(__import__(module))
            WriteDebug( 'Loaded: %s' % module )
        except Exception as eX:
            WriteDebug( 'Failed Loading: %s => %s' % (module, eX))

#===========================================================
# Then, for each module, we store all the Providers under it.
#===========================================================
for providerModule in TotalProviderModules:
    storeISubProviderImplementations(providerModule)

#===========================================================
# Last, insert the providers to RelevantProvidersOrdered. The 
# queue is sorted, so calling the getNextProvider method will 
# give the next provider following the configured order.
#===========================================================
providers_lang_order = getSelectedLanguages()
providers_name_order = getSelectedProviders()

for provider_lang in providers_lang_order:
    for provider_name in providers_name_order:
        provider = getSubProviderByName\
            (buildSubProviderName(provider_lang, provider_name))
        # If we succeeded - there's such provider (lang and name combination).
        if provider:
            RelevantProvidersOrdered.put_nowait(provider)
