import sys
import os
import time

import Utils
if Utils.IsWindowPlatform():
    import RegistryHandler
import Settings
from Settings import Config




EXTENSIONS = []
#Location of SubiT.exe from the installation path - 
#special extraction because we're inside the zipfile
EXE_LOCATION            = os.path.join(Utils.PROGRAM_DIR_PATH, 'SubiT.exe')
REG_KEYS_CONFIG_DELIMITER = '|'

def getExtList(reload=False):
    global EXTENSIONS
    if (reload or not len(EXTENSIONS)):
            EXTENSIONS = Config.SubiTConfig.Singleton().getStr('Registry', 'keys').split(REG_KEYS_CONFIG_DELIMITER)
    return EXTENSIONS
    
def setExtList(extList):
    Config.SubiTConfig.Singleton().setValue('Registry', 'keys', REG_KEYS_CONFIG_DELIMITER.join(extList))
    getExtList(True)



#===============================================================================
# Will register one extension to the right key
#===============================================================================
def register(extension):
    (error_code, hKey) = RegistryHandler.getRelevantKey(extension)
    
    #Check if we're not registered under the given key
    if not RegistryHandler.isSubiTRegistered(extension):
        if error_code == RegistryHandler.ERROR_SUCCESS: #Success
            error_code = RegistryHandler.register(hKey, EXE_LOCATION)
        else:
            Utils.WriteDebug('getRelevantKey error_code: %s' % error_code)
    Utils.WriteDebug('Registration for ext: %s => %s' % (extension, 'Success' if not error_code else 'Failed'))
    return error_code


#=======================================================================
# Runs regiser on all extension under EXTENSIONS[]
#=======================================================================
def register_all():
    # TODO: check if we got error_code == ERROR_ACCESS_DENIED and if so, ask the user to run us as administrator
    try:
        for ext in getExtList():
            #If we got access_denied error
            if register(ext) == RegistryHandler.ERROR_ACCESS_DENIED:
                #Tell the user we need more privilages, and return from function
                Utils.GuiInstance.getSettings().tellUserToRunAsAdministrator()
                return
        Config.SubiTConfig.Singleton().setValue('Registry', 'register_extensions', True)
        Config.SubiTConfig.Singleton().save()
    except Exception as eX:
        Utils.WriteDebug('Registry exception: %s' % eX)
        
        
#===============================================================================
# Will un-register one extension from the right key
#===============================================================================
def unregister(extension):
    (error_code, hKey) = RegistryHandler.getRelevantKey(extension)

    #Check if we're registered under the given key
    if RegistryHandler.isSubiTRegistered(extension):
        if error_code == RegistryHandler.ERROR_SUCCESS: #Success
            error_code = RegistryHandler.unregister(hKey)
        else:
            Utils.WriteDebug('getRelevantKey error_code: %s' % error_code)
    Utils.WriteDebug('Remove registration for ext: %s => %s' % (extension, 'Success' if not error_code else 'Failed'))
    return error_code

#=======================================================================
# Runs unregiser on all extension under EXTENSIONS[]
#=======================================================================
def unregister_all():
    # TODO: check if we got error_code == ERROR_ACCESS_DENIED and if so, ask the user to run us as administrator
    try:
        for ext in getExtList():
            #If we got access_denied error
            if unregister(ext) == RegistryHandler.ERROR_ACCESS_DENIED:
                #Tell the user we need more privilages, and return from function
                Utils.GuiInstance.getSettings().tellUserToRunAsAdministrator()
                return
        Config.SubiTConfig.Singleton().setValue('Registry', 'register_extensions', False)
        Config.SubiTConfig.Singleton().save()
    except Exception as eX:
        Utils.WriteDebug('Registry exception: %s' % eX)

#===============================================================================
# In case of directly running this script - should'nt happen...
#===============================================================================
if __name__ == '__main__':
    type = sys.argv[1] if len(sys.argv) > 1 else ''
    
    types = {   '-register': lambda: register_all(),
                '-unregister': lambda: unregister_all() }
    if type in types:
        types[type]()
        register_all()
    else:
        print ('Usage: Registry.py [-register/-unregister]')
        raise (Exception, 'Unknown parameter')

