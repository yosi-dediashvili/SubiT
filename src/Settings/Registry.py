import sys
import os
import time
if os.name == 'nt':
    import RegistryHandler



EXTENSIONS = []
#Location of SubiT.exe from the installation path - 
#special extraction because we're inside the zipfile
SETTINGS_DIR_LOCATION   = os.path.split(os.path.abspath(__file__))[0].replace('\\library.zip\\Settings', '')
EXE_LOCATION            = os.path.join(SETTINGS_DIR_LOCATION.replace('Settings', ''), 'SubiT.exe')
CONFIG_FILE_NAME        = os.path.join(SETTINGS_DIR_LOCATION, 'ext.cfg')

def getExtList(reload=False):
    global EXTENSIONS
    if (reload or not len(EXTENSIONS)):
        if os.path.exists(CONFIG_FILE_NAME):
            EXTENSIONS = [i.rstrip() for i in open(CONFIG_FILE_NAME, 'r').readlines()]
        else:
            EXTENSIONS = ['.avi', '.mkv', '.wmv', '.mp4', 'Directory']
    return EXTENSIONS
    
def setExtList(extList):
    with open(CONFIG_FILE_NAME, 'w') as conf_file:
        for ext in extList:
            conf_file.write('%s\n' % ext)
    getExtList(True)



#===============================================================================
# Will register one extension to the right key
#===============================================================================
def register(extension):
    (result, hKey) = RegistryHandler.getRelevantKey(extension)
    if result == 0: #Success
        RegistryHandler.register(hKey, EXE_LOCATION)
    print ('Registration for ext: %s => %s' % (extension, 'Success' if not result else 'Failed'))
#=======================================================================
# Runs regiser on all extension under EXTENSIONS[]
#=======================================================================
def register_all():
    for ext in getExtList():
        register(ext)
        
#===============================================================================
# Will un-register one extension from the right key
#===============================================================================
def unregister(extension):
    (result, hKey) = RegistryHandler.getRelevantKey(extension)
    if result == 0: #Success
        RegistryHandler.unregister(hKey)
    print ('Remove registration for ext: %s => %s' % (extension, 'Success' if not result else 'Failed'))
#=======================================================================
# Runs unregiser on all extension under EXTENSIONS[]
#=======================================================================
def unregister_all():
    for ext in getExtList():
        unregister(ext)



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

