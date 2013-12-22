import sys
import os
import subprocess
import time

EXTENSIONS = ['.avi', '.mkv', '.wmv', '.mp4', 'Directory']
#Location of SubiT.exe from the installation path - 
#special extraction because we're inside the zipfile

EXE_LOCATION = os.path.join(os.path.split(os.path.abspath(__file__))[0]
                                                .replace('\\library.zip', '')
                                                , 'SubiT.exe')
#Location of SubiTRegister.exe from the installation path - 
#special extraction because we're inside the zipfile
REG_LOCATION = os.path.join(os.path.split(os.path.abspath(__file__))[0]
                                                  .replace('\\library.zip', '')
                                                  , 'SubiTRegister.exe')

#===============================================================================
# Will register one extension to the right key
#===============================================================================
def register(extension):
    command = '\"%s\" -register %s \"%s\"' % (REG_LOCATION, extension, EXE_LOCATION)
    with open('logfile.log', 'a') as log:
        log.write('%s -> command: %s\n' % (time.ctime(), command))
        log.write('\t%s\n' % subprocess.check_output(command, stderr=subprocess.PIPE, stdin=subprocess.PIPE))
#=======================================================================
# Runs regiser on all extension under EXTENSIONS[]
#=======================================================================
def register_all():
    for ext in EXTENSIONS:
        register(ext)
        
#===============================================================================
# Will un-register one extension from the right key
#===============================================================================
def unregister(extension):
    command = '\"%s\" -unregister %s' % (REG_LOCATION, extension)
    with open('logfile.log', 'a') as log:
        log.writelines('%s -> command: %s\n' % (time.ctime(), command))
        log.write('\t%s\n' % subprocess.check_output(command, stderr=subprocess.PIPE, stdin=subprocess.PIPE))
#=======================================================================
# Runs unregiser on all extension under EXTENSIONS[]
#=======================================================================
def unregister_all():
    for ext in EXTENSIONS:
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
        print 'Usage: Registry.py [-register/-unregister]'
        raise Exception, 'Unknown parameter' 











#===============================================================================
# OLD Code - before SubiTRegister.exe...
#===============================================================================

#import _winreg


#KEY_NAME = 'SubiT'
#
#CURRENT_USER_TEMPLATE       = r'SOFTWARE\Classes\{0}'
#USER_CHOICE_KEY_TEMPLATE    = r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{0}\UserChoice'
#def keyExists(key, sub_key, ex = False):
#    try:
#        if not ex: #query default_value (Empty)
#            return (True, _winreg.QueryValue(key, sub_key)) #if we reach this line, it means that query was successful
#        else:
#            return (True, _winreg.QueryValueEx(key, sub_key)[0])
#    except WindowsError as we:
#        if we.errno == 2: #system cannot find the file specified (missing key...)
#            return (False, None)
#        else:
#            raise we #in any other error, we throw
#
##===============================================================================
## This function figures out the relevant key for context menu registration.
## Logic: 
##    1. look at USER_CHOICE_KEY - if empty, go to 2, else, use the progid value 
##       as the key at CURRENT_USER path
##    2. look at CURRENT_USER default_value - if empty, go to 3, else use the 
##       default_value as the key at HKEY_LOCAL_MACHINE / CURRENT_USER
##    3. look at HKEY_LOCAL_MACHINE - if empty, use it, else use the default_value
##       as the key
##===============================================================================
#def findUsableKey(extension):
#    (cu_keyExists, cu_defaultValue) = keyExists(_winreg.HKEY_CURRENT_USER, CURRENT_USER_TEMPLATE.format(extension))
#    (cr_keyExists, cr_defaultValue) = keyExists(_winreg.HKEY_CLASSES_ROOT, extension)
#    (uc_keyExists, uc_defaultValue) = keyExists(_winreg.HKEY_CURRENT_USER, USER_CHOICE_KEY_TEMPLATE.format(extension))
#    
#    #If all keys are empty
#    if not (cu_keyExists and cr_keyExists and uc_keyExists):
#        return CURRENT_USER_TEMPLATE.format(extension)
#    #if userchoice key is not empty, we use the value
#    if uc_keyExists:
#        with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, USER_CHOICE_KEY_TEMPLATE.format(extension)) as uc_key:
#            (uc_pi_keyExists, uc_pi_progId) = keyExists(uc_key, 'Progid', True)
#            if uc_pi_keyExists and len(uc_pi_progId):
#                return CURRENT_USER_TEMPLATE.format(uc_pi_progId)
#            
#    if cu_keyExists and len(cu_defaultValue):
#        return CURRENT_USER_TEMPLATE.format(cu_defaultValue)
#    else:
#        return CURRENT_USER_TEMPLATE.format(cr_defaultValue)
#    
#def register(extension):
#    try:
#        with _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, findUsableKey(extension)) as ext_key:
#            with _winreg.CreateKey(ext_key, 'shell') as shell_key:
#                with _winreg.CreateKey(shell_key, KEY_NAME) as keyname_key:
#                    with _winreg.CreateKey(keyname_key, 'command') as command_key:
#                        _winreg.SetValue(command_key, '', _winreg.REG_SZ, '\"{0}\" \"%1\"'.format(EXE_LOCATION))
#        print 'Successfully created key for extension: %s' % extension
#    except WindowsError as we:
#        if we.errno == 2:
#                print 'Key doesnt exists for extension: %s' % extension
#        else:
#            print 'Failure while creating key for extension: %s' % extension
#            raise we
#def unregister(extension):
#    try:
#        with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, findUsableKey(extension)) as ext_key:
#            with _winreg.OpenKey(ext_key, 'shell') as shell_key:
#                with _winreg.OpenKey(shell_key, KEY_NAME) as keyname_key:
#                    _winreg.DeleteKey(keyname_key, 'command')
#                _winreg.DeleteKey(shell_key, KEY_NAME)
#        print 'Successfully deleted key for extension: %s' % extension
#    except WindowsError as we:
#        if we.errno == 2:
#            print 'Key doesnt exists for extension: %s' % extension
#        else:
#            raise we

