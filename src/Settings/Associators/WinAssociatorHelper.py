import Utils
if Utils.IsPython3():
    import winreg
else:
    import _winreg as winreg
import ctypes
from ctypes import byref, wintypes
import os
import sys

from Settings.Config import SubiTConfig

WriteDebug = Utils.WriteDebug

# ============================================================================ #
# Predefined CONST and Function taken from windows lib                         #
# ============================================================================ #
ASSOCF_INIT_IGNOREUNKNOWN = 0x00000400 
ASSOCKEY_CLASS            = 3

REG_SZ          = winreg.REG_SZ
REG_EXPAND_SZ   = winreg.REG_EXPAND_SZ

ERROR_SUCCESS           = 0x0
ERROR_ACCESS_DENIED     = 0x5
ERROR_PATH_NOT_FOUND    = 0x2

KEY_READ    = 0x20019
KEY_WRITE   = 0x20006

NULL = 0x0

# AccessDenied from ShellExecute
SE_ERR_ACCESSDENIED = 0x4
# Program start cmd for ShellExecute
SW_SHOWNORMAL = 0x1

#Win32 api Functions. We use unicode functions (same as python's)
SHDeleteKey     = None
RegDeleteTree   = None
AssocQueryKey   = None
ShellExecute    = None
RegCloseKey     = None
RegOpenKeyEx    = None
RegCreateKeyEx  = None
RegSetValueEx   = None
RegSetValue     = None

if Utils.IsVistaOrLater():
    RegDeleteTree = ctypes.windll.advapi32.RegDeleteTreeW
else:
    SHDeleteKey = ctypes.windll.shlwapi.SHDeleteKeyW

AssocQueryKey   = ctypes.windll.shlwapi.AssocQueryKeyW
ShellExecute    = ctypes.windll.shell32.ShellExecuteW
RegCloseKey     = ctypes.windll.advapi32.RegCloseKey
RegOpenKeyEx    = ctypes.windll.advapi32.RegOpenKeyExW
RegCreateKeyEx  = ctypes.windll.advapi32.RegCreateKeyExW
RegSetValueEx   = ctypes.windll.advapi32.RegSetValueExW
RegSetValue     = ctypes.windll.advapi32.RegSetValueW

# Path of subit under some extension in the registry (shell\SubiT)
_SUBIT_PATH = None
# ============================================================================ #
# ============================================================================ #

# ============================================================================ #
# Global functions                                                             #
# ============================================================================ #
def ExecuteWithHigherPrivilages(param):
    """ Load SubiT in elevated privilages. Return True on success, in any 
        other case, return False 
    """
    #HINSTANCE ShellExecute(
    #    __in_opt  HWND hwnd,
    #    __in_opt  LPCTSTR lpOperation,
    #    __in      LPCTSTR lpFile,
    #    __in_opt  LPCTSTR lpParameters,
    #    __in_opt  LPCTSTR lpDirectory,
    #    __in      INT nShowCmd
    #    );
    # Return value higher than 32, is Success
    if len(sys.argv) > 2 and sys.argv[2] == '-elevated':
        return False
    
    hwnd         = NULL
    lpOperation  = _as_unicode('runas')
    lpFile       = _as_unicode(os.path.join(Utils.GetProgramDir(), 'SubiT.exe'))
    lpParameters = _as_unicode(param + ' -elevated')
    lpDirectory  = _as_unicode(Utils.GetProgramDir())
    nShowCmd     = SW_SHOWNORMAL

    shell_exec_params = \
        (hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd)

    error_border = 32
    return_value = 100
    WriteDebug('ShellExecute: %s, %s, %s, %s, %s, %s' % shell_exec_params)
    return_value = ShellExecute(*shell_exec_params)
    WriteDebug('ShellExecute return code: %s' % return_value)
    return return_value > error_border

def _as_unicode(str_content):
    """ Return the string in unicode format """
    if Utils.IsPython3():
        return bytes(str_content, 'utf-8').decode('utf-8')
    else:
        return str_content.decode('utf-8')

def SetSubitPath(subit_menu_text):
    """ Set path to registry under a given key. The path is in unicode. """
    global _SUBIT_PATH
    _SUBIT_PATH = _as_unicode('shell\\%s' % subit_menu_text)

def GetSubitPath():
    """ Get path to registry under a given key. The path is in unicode. """
    global _SUBIT_PATH
    if not _SUBIT_PATH:
        WriteDebug('_SUBIT_PATH is not set!')
    else:
        WriteDebug('_SUBIT_PATH is: %s' % _SUBIT_PATH)
    return _SUBIT_PATH

def getRelevantKeyForExt( ext ):
    """ Retrieve handle to the relevant key for the specific ext """
    WriteDebug('Calling AssocQueryKey for: %s' % ext)
    ext = _as_unicode(ext)
    hKey = wintypes.HKEY()
    error_code = AssocQueryKey\
        (ASSOCF_INIT_IGNOREUNKNOWN, ASSOCKEY_CLASS, ext, NULL, byref(hKey))
    WriteDebug('AssocQueryKey error_code: %s' % error_code)
    return (error_code, hKey)

def isSubiTRegistered(ext):
    """ Check if we're registered on the given extension """
    WriteDebug('Checking if SubiT is registered')
    result = False
    ext = _as_unicode(ext)
    if GetSubitPath():
        (error_code, hKey) = getRelevantKeyForExt(ext)
        subitKey = wintypes.HKEY()
        if error_code == ERROR_SUCCESS:
            open_error_code = RegOpenKeyEx\
                (hKey, GetSubitPath(), NULL, KEY_READ, byref(subitKey))
            WriteDebug('RegOpenKeyEx error_code: %s' % open_error_code)
            result = (open_error_code == ERROR_SUCCESS)
        WriteDebug('SubiT is registered? %s' % result)
        RegCloseKey(subitKey)
        RegCloseKey(hKey)
    return result
    
# ============================================================================ #
# Association functions                                                        #
# ============================================================================ #
def register_under_hkey(hKey):
    """ Function to register SubiT under the given registry key, using the 
        path given to the SubiT.exe file """

    exe_path = os.path.join(Utils.GetProgramDir(), 'SubiT.exe')
    reg_defaule_value_value = _as_unicode('"%s" "%%1"' % exe_path)
    # Path to the icon resource: <exe_path>,<icon_index>
    reg_icon_value          = _as_unicode(exe_path + ',0')
    subitHKey               = wintypes.HKEY()
    return_code             = ERROR_SUCCESS

    if GetSubitPath():
        #Open/Create SubiT's key
        retCode = RegCreateKeyEx(hKey, GetSubitPath(), NULL, NULL, NULL, 
                                 KEY_WRITE, NULL, byref(subitHKey), NULL)
        #If we succeeded to gain access
        if retCode == ERROR_SUCCESS:
            #Register the default value for SubiT key
            reg_default_value_err_code = RegSetValue\
                (subitHKey, _as_unicode('command'), REG_SZ, 
                 reg_defaule_value_value, NULL)
            #Set the icon for SubiT's key
            reg_icon_err_code = RegSetValueEx\
                (subitHKey, _as_unicode('Icon'), NULL, REG_SZ, 
                 # Unicode length is 2 Bytes per char, we need string length + 
                 # the null terminate char
                 _as_unicode(reg_icon_value), len(reg_icon_value) * 2 + 2)
                                    
            WriteDebug('reg_default_value_err_code: %s' % reg_default_value_err_code)
            WriteDebug('reg_icon_err_code: %s' % reg_icon_err_code)
            # Return bitwise oR for of both registration                                            
            return_code = reg_default_value_err_code | reg_icon_err_code
        else:
            WriteDebug('Retrun code from RegCreateKeyEx is %s' % retCode)
            return_code = retCode
    
    RegCloseKey(subitHKey)
    RegCloseKey(hKey)
    
    WriteDebug('return_code is %s' % return_code)
    return return_code

def register_ext(ext):
    """ Will register one extension to the right key """
    (error_code, hKey) = getRelevantKeyForExt(ext)
    
    #Check if we're not registered under the given key
    if not isSubiTRegistered(ext):
        if error_code == ERROR_SUCCESS: #Success
            error_code = register_under_hkey(hKey)
        else:
            WriteDebug('getRelevantKeyForExt error_code: %s' % error_code)
    WriteDebug('Registration for ext: %s => %s' % (ext, 'Success' if not error_code else 'Failed'))
    return error_code

def register_all(command):
    """ Runs regiser on all extension in config """
    try:
        last_error_code = ERROR_SUCCESS
        for ext in Utils.GetMoviesExtensions():
            #If we got access_denied error
            last_error_code = register_ext(ext)
            if last_error_code == ERROR_ACCESS_DENIED:
                WriteDebug('Got Access Denied, Elevating!')
                break

        if last_error_code == ERROR_ACCESS_DENIED:
            if ExecuteWithHigherPrivilages(command):
                WriteDebug('Elevation succeeded!')
            else:
                WriteDebug('Elevation failed!')
                return False

        SubiTConfig.Singleton().setValue\
            ('Association', 'associate_extensions', True)
        return True
    except Exception as eX:
        WriteDebug('Registry exception: %s' % eX)
        return False

# ============================================================================ #
# UnAssociation functions                                                      #
# ============================================================================ #
def unregister_under_hkey( hKey ):
    """ Function to unregister SubiT from the given registry key """
    error_code  = ERROR_SUCCESS
    subitHKey   = wintypes.HKEY()

    if GetSubitPath():
        # Open/Create SubiT's key
        error_code = RegOpenKeyEx\
            (hKey, GetSubitPath(), NULL, KEY_WRITE, byref(subitHKey))
        # If we succeeded to gain access
        if error_code == ERROR_SUCCESS:
            if Utils.IsVistaOrLater():
                error_code = RegDeleteTree(hKey, GetSubitPath())
            elif Utils.IsWindowPlatform():
                error_code = SHDeleteKey(hKey, GetSubitPath())

        WriteDebug('unregister->error_code for RegDeleteTree/SHDeleteKey: %s' % error_code)

    RegCloseKey(hKey)
    RegCloseKey(subitHKey)
    
    return error_code

def unregister_ext(ext):
    """ Will un-register one extension from the right key """
    (error_code, hKey) = getRelevantKeyForExt(ext)

    # Check if we're registered under the given key
    if isSubiTRegistered(ext):
        if error_code == ERROR_SUCCESS: 
            error_code = unregister_under_hkey(hKey)
        else:
            WriteDebug('getRelevantKeyForExt error_code: %s' % error_code)
    WriteDebug('Remove registration for ext: %s => %s' % (ext, 'Success' if not error_code else 'Failed'))
    return error_code

def unregister_all(command):
    """ Runs unregiser on all extension in config """
    try:
        last_error_code = ERROR_SUCCESS
        for ext in Utils.GetMoviesExtensions():
            # If we got access_denied error
            last_error_code = unregister_ext(ext)
            if last_error_code == ERROR_ACCESS_DENIED:
                WriteDebug('Got Access Denied, Elevating!')
                break

        if last_error_code == ERROR_ACCESS_DENIED:
            if ExecuteWithHigherPrivilages(command):
                WriteDebug('Elevation succeeded!')
            else:
                WriteDebug('Elevation failed!')
                return False

        SubiTConfig.Singleton().setValue\
            ('Association', 'associate_extensions', False)
        return True
    except Exception as eX:
        WriteDebug('Registry exception: %s' % eX)
        return False
