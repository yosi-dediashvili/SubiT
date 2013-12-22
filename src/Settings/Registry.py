import sys
import os
import time
if os.name == 'nt':
    import RegistryHandler

import Settings
from Settings import Config
import Utils



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
    (result, hKey) = RegistryHandler.getRelevantKey(extension)
    if result == 0: #Success
        RegistryHandler.register(hKey, EXE_LOCATION)
    Utils.WriteDebug('Registration for ext: %s => %s' % (extension, 'Success' if not result else 'Failed'))
#=======================================================================
# Runs regiser on all extension under EXTENSIONS[]
#=======================================================================
def register_all():
    for ext in getExtList():
        register(ext)
    Config.SubiTConfig.Singleton().setValue('Registry', 'register_extensions', True)
    Config.SubiTConfig.Singleton().save()
        
#===============================================================================
# Will un-register one extension from the right key
#===============================================================================
def unregister(extension):
    (result, hKey) = RegistryHandler.getRelevantKey(extension)
    if result == 0: #Success
        RegistryHandler.unregister(hKey)
    Utils.WriteDebug('Remove registration for ext: %s => %s' % (extension, 'Success' if not result else 'Failed'))
#=======================================================================
# Runs unregiser on all extension under EXTENSIONS[]
#=======================================================================
def unregister_all():
    for ext in getExtList():
        unregister(ext)
    Config.SubiTConfig.Singleton().setValue('Registry', 'register_extensions', False)
    Config.SubiTConfig.Singleton().save()


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

