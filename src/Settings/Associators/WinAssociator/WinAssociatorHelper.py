import Utils

import _winreg as winreg
import ctypes
from ctypes import byref, wintypes
import os
import sys

from Settings.Config import SubiTConfig

WriteDebug = Utils.WriteDebug

if Utils.Is64BitWindows():
    DLL_NAME = 'SubiT.ShellExt.64.dll'
    _platform_specific_dir = '64'
else:
    DLL_NAME = 'SubiT.ShellExt.32.dll'
    _platform_specific_dir = '32'

CONTEXT_MENU_HANDLER_FULL_PATH = os.path.join\
    (Utils.GetProgramDir(), 'Settings', 'Associators', 
     'WinAssociator', _platform_specific_dir, DLL_NAME)


CURRENT_ASSOCIATION_COMMAND = None
ELEVATION_COMMAND = '-elevated'

# ============================================================================ #
# Predefined CONST and Function taken from windows lib                         #
# ============================================================================ #
ASSOCF_NOUSERSETTINGS     = 0x00000010
ASSOCF_INIT_IGNOREUNKNOWN = 0x00000400 
ASSOCKEY_CLASS            = 3

REG_SZ          = winreg.REG_SZ
REG_EXPAND_SZ   = winreg.REG_EXPAND_SZ

RRF_RT_REG_EXPAND_SZ = 0x00000004
RRF_RT_REG_SZ        = 0x00000002

S_OK = 0x00000000

ERROR_SUCCESS           = 0x0
ERROR_ACCESS_DENIED     = 0x5
ERROR_PATH_NOT_FOUND    = 0x2

KEY_READ    = 0x20019
KEY_WRITE   = 0x20006
KEY_QUERY_VALUE = 0x0001


NULL = 0x0

# AccessDenied from ShellExecute
SE_ERR_ACCESSDENIED = 0x4
# Program start cmd for ShellExecute
SW_SHOWNORMAL = 0x1

#Win32 api Functions. We use unicode functions (same as python's)
SHDeleteKey     = None
AssocQueryKey   = None
ShellExecute    = None
RegCloseKey     = None

    
SHDeleteKey     = ctypes.windll.shlwapi.SHDeleteKeyW
AssocQueryKey   = ctypes.windll.shlwapi.AssocQueryKeyW
ShellExecute    = ctypes.windll.shell32.ShellExecuteW
RegCloseKey     = ctypes.windll.advapi32.RegCloseKey
RegCreateKeyEx  = ctypes.windll.advapi32.RegCreateKeyExW
RegSetValue     = ctypes.windll.advapi32.RegSetValueW


# ============================================================================ #
# ============================================================================ #

def InitCurrentAssociationCommand(command):
    """ This function should be called when starting to use the 
        WinAssocaitorHandler in the current session, i.e when the interface's
        SetAssociation/RemoveAssociation function called. The function is 
        needed for the AccessDeniedHandler decotrator.
    """
    global CURRENT_ASSOCIATION_COMMAND
    CURRENT_ASSOCIATION_COMMAND = command

def AccessDeniedHandler(func):
    """ The function is a decorator for all the registry access function. The
        purpose of this function is to handle a case where the function return
        an access_denied value that is set to true. In such case, the function
        will restart the program but with higher privilages (see more about 
        that in the docs of ExecuteWithHigherPrivilages() function.

        Any function that uses this decorator should return a tuple where:
        param1 = access_denied value.
        param2 = real value (might be tuple also if you like).

        If the access_denied is true, the function will return None instead of
        the return_value from the underlying method.
    """
    WriteDebug('AccessDeniedHandler set for: %s' % func.__name__)
    def wrapper(*args, **kwargs):
        WriteDebug('Calling %s with: [%s, %s]' % (func.__name__, args, kwargs))
        access_denied, return_value = func(*args, **kwargs)
        WriteDebug('access_denied: %s' % access_denied)
        WriteDebug('return_value: %s' % return_value)

        if access_denied:
            WriteDebug('access_denied is True, calling ExecuteWithHigherPrivilages()')
            if ExecuteWithHigherPrivilages(CURRENT_ASSOCIATION_COMMAND):
                WriteDebug('Elevation succeeded.')
            else:
                WriteDebug('Elevation failed.')
            return None

        return return_value
    return wrapper

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
    if ELEVATION_COMMAND in sys.argv:
        return False
    
    hwnd         = NULL
    lpOperation  = _as_unicode('runas')
    lpFile       = _as_unicode(os.path.join(Utils.GetProgramDir(), os.path.split(sys.executable)[1]))
    lpParameters = _as_unicode(param + ' ' + ELEVATION_COMMAND)
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
    if str_content is not None and type(str_content) is str:
        return str_content.decode('utf-8')
    else:
        return str_content

# Registry access function
def is_clsid_registered_in_hkcr(clsid):
    """ Check if the given clsid is registered under hkcr\clsid. """
    WriteDebug('Checking if the clsid is registered: %s' % clsid)
    clsid_path = _as_unicode('CLSID\\' + clsid)
    return is_key_exists_in_hkcr(clsid_path)

@AccessDeniedHandler
def get_relevant_key_handle_for_extension_association(file_extension):   
    """ Return the relevant key handle for associating with a given file
        extensions. The return value is a tuple of error_code and a key handle.
    """
    WriteDebug('Calling AssocQueryKey for: %s' % file_extension)
    file_extension = _as_unicode(file_extension)

    key = wintypes.HKEY()
    error_code = AssocQueryKey\
        (ASSOCF_INIT_IGNOREUNKNOWN, ASSOCKEY_CLASS, 
         file_extension, NULL, byref(key))
    WriteDebug('AssocQueryKey error_code: %s' % error_code)

    access_denied = False
    return_value = None

    if error_code == S_OK:
        WriteDebug('Successfully called to AssocQueryKey, got HKEY.')
        return_value = key.value
    elif error_code == ERROR_ACCESS_DENIED:
        WriteDebug('Failed calling AssocQueryKey, got ACCESS_DENIED.')
        access_denied = True
    else:
        WriteDebug('Failed calling AssocQueryKey: %s.' % error_code)

    # That is the return value signature for the AcessDeniedHandler decorator.
    return access_denied, return_value

def set_hkcr_registry_key_and_value(sub_key, value_name, value_data):
    """ Will set the given value_data under the given value_name in the given 
        sub_key under HKEY_CLASSES_ROOT. The first item indicates whether the
        operation succeeded, and the second whether the error (if failed) was
        an access denied.
    """
    WriteDebug('set_hkcr_registry_key_and_value() called.')
    WriteDebug('sub_key: %s, value_name: %s, value_data: %s' % (sub_key, value_name, value_data))
    return set_registry_key_and_value\
        (winreg.HKEY_CLASSES_ROOT, sub_key, value_name, value_data)

def set_hkcu_registry_key_and_value(sub_key, value_name, value_data):
    """ Will set the given value_data under the given value_name in the given 
        sub_key under HKEY_CURRENT_USER. The first item indicates whether the
        operation succeeded, and the second whether the error (if failed) was
        an access denied.
    """
    WriteDebug('set_hkcu_registry_key_and_value() called.')
    WriteDebug('sub_key: %s, value_name: %s, value_data: %s' % (sub_key, value_name, value_data))
    return set_registry_key_and_value\
        (winreg.HKEY_CURRENT_USER, sub_key, value_name, value_data)

@AccessDeniedHandler
def set_registry_key_and_value(\
    root_key, sub_key, value_name, value_data, close_root = False):
    """ Will set the given value data under the value_name in the sub_key under
        the root_key. If close_root is True, RegCloseKey is called for the 
        root_key. The a tuple of boolean. The first item indicates whether the
        operation succeeded, and the second whether the error (if failed) was
        an access denied.
    """
    WriteDebug('set_registry_key_and_value() called.')
    WriteDebug('root_key: %s' % root_key)
    WriteDebug('sub_key: %s' % sub_key)
    WriteDebug('value_name: %s' % value_name)
    WriteDebug('value_data: %s' % value_data)

    access_denied   = False
    return_value    = False

    sub_key = _as_unicode(sub_key)
    value_name = _as_unicode(value_name)
    value_data = _as_unicode(value_data)

    try:
        WriteDebug('Calling to CreateKeyEx.')
        # Open the key (if the 64 bit os is present, the 64 bit key will be 
        # opened).
        with winreg.CreateKeyEx(
            root_key, 
            sub_key, 
            0, 
            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:

            WriteDebug('CreateKeyEx called successfully, calling to SetValue.')
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
            return_value = True

    except WindowsError as wE:
        WriteDebug('Failed (Windows error) calling to CreateKeyEx: %s' % wE.strerror)
        access_denied = wE.winerror == ERROR_ACCESS_DENIED
    except Exception as eX:
        WriteDebug('Failed (unknown error) calling to CreateKeyEx: %s' % eX)
        access_denied = False
    finally:
        if close_root:
            if root_key is winreg.HKEYType:
                winreg.CloseKey(root_key)
            else:
                RegCloseKey(root_key)

    # That is the return value signature for the AcessDeniedHandler decorator.
    return access_denied, return_value
    

def delete_hkcr_registry_key_tree(sub_key):
    """ Will delete the given sub_key from HKEY_CLASSES_ROOT. The function 
        return a win32 error value. 
    """
    WriteDebug('delete_hkcr_registry_key_tree() called for sub_key: %s' % sub_key)
    return delete_registry_key_tree(winreg.HKEY_CLASSES_ROOT, sub_key)

def delete_hkcu_registry_key_tree(sub_key):
    """ Will delete the given sub_key from HKEY_CURRENT_USER. The function 
        return a win32 error value. 
    """
    WriteDebug('delete_hkcu_registry_key_tree() called for sub_key: %s' % sub_key)
    return delete_registry_key_tree(winreg.HKEY_CURRENT_USER, sub_key)

@AccessDeniedHandler
def delete_registry_key_tree(root_key, sub_key, close_root = False):
    """ Will delete the given sub_key from root_key. The function return a 
        win32 error value. If close_root is True, RegCloseKey is called for 
        the root_key.
    """
    WriteDebug('delete_registry_key_tree() called for sub_key: %s under root_key: %s' % (sub_key, root_key))

    def traverse(root, key, list):
        """ The function will create a list containing all the sub-keys under 
            the root + key path. The keys are stored in the list parameter.
        """
        # We open the key in read-only mode, and without WOW64 reflection.
        hKey = winreg.OpenKey(
            root, 
            key, 
            0, 
            winreg.KEY_WOW64_64KEY | winreg.KEY_READ)
        try:
            i = 0
            while 1:
                strFullSubKey = ""
                try:
                    strSubKey = winreg.EnumKey(hKey, i)
                    strFullSubKey = key + "\\" + strSubKey
                except WindowsError:
                    hKey.Close()
                    return;
 
                traverse(root, strFullSubKey, list)
                list.append(strFullSubKey)

                i += 1
        except WindowsError as eX:
            WriteDeubug('delete_registry_key_tree.traverse() failed: %s' % eX)
 
        hKey.Close();
 
    def reg_delete_key(root, key):
        """ The function will delete the key, and all the sub-keys under it.
            The function can safely be used with key opened without WOW64
            reflection.
        """
        global list;
        list = list()
        # Retrieve all the sub-keys.
        traverse(root, key, list)
        # Delete all the sub-keys.
        for item in list:
            if Utils.IsVistaOrLater():
                winreg.DeleteKeyEx(root, item, winreg.KEY_WOW64_64KEY, 0)
            else:
                winreg.DeleteKey(root, item)
        # Finally, delete the key (the only one that was left).
        if Utils.IsVistaOrLater():
            winreg.DeleteKeyEx(root, key, winreg.KEY_WOW64_64KEY, 0)
        else:
            winreg.DeleteKey(root, key)
    
    if close_root:
        RegCloseKey(root_key)

    access_denied = ERROR_ACCESS_DENIED
    return_value = ERROR_SUCCESS

    try:
        WriteDebug('Calling reg_delete_key.')
        reg_delete_key(root_key, sub_key)
        return_value = True
        WriteDebug('Key deleted sucessfully.')

    except WindowsError as  wE:
        WriteDebug('Failed (Windows error) calling to DeleteKeyEx: %s' % wE.strerror)
        access_denied = wE.winerror == ERROR_ACCESS_DENIED
    except Exception as eX:
        WriteDebug('Failed in accessing the key, key does not exists: %s' % eX)
        return_value = False

    return access_denied, return_value

def is_key_exists_in_hkcr(sub_key):
    """ Check if the given sub_key is under the HKEY_CLASS_ROOT. """
    WriteDebug('is_key_exists_in_hkcr() called for sub_key: %s' % sub_key)
    return is_key_exists(winreg.HKEY_CLASSES_ROOT, sub_key)

def is_key_exists_in_hkcu(sub_key):
    """ Check if the given sub_key is under the HKEY_CURRENT_USER. """
    WriteDebug('is_key_exists_in_hkcu() called for sub_key: %s' % sub_key)
    return is_key_exists(winreg.HKEY_CURRENT_USER, sub_key)

@AccessDeniedHandler
def is_key_exists(root_key, sub_key, close_root = False):
    """ Check if the sub_key exists under the given root key. If close_root
        is True, winreg.CloseKey is called for the root_key.
    """
    WriteDebug('is_key_exists() called for sub_key: %s' % sub_key)

    return_value = False
    access_denied = False

    try:
        WriteDebug('Calling winreg.OpenKeyEx.')
        key = winreg.OpenKeyEx\
            (root_key, _as_unicode(sub_key), 0, 
             winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        return_value = True
        key.Close()
        WriteDebug('The key exists.')

    except WindowsError as  wE:
        WriteDebug('Failed (Windows error) calling to OpenKeyEx: %s' % wE.strerror)
        access_denied = wE.winerror == ERROR_ACCESS_DENIED
    except Exception as eX:
        WriteDebug('Failed in accessing the key, key does not exists: %s' % eX)
        return_value = False
    finally:
        if close_root:
            if root_key is winreg.HKEYType:
                winreg.CloseKey(root_key)
            else:
                RegCloseKey(root_key)

    return access_denied, return_value

def get_hkcr_key_value_data(sub_key, value):
    """ Return the data stored under the fiven sub_key and value in the root 
        HKEY_CLASSES_ROOT.
    """
    WriteDebug('get_hkcr_key_value_data() called for sub_key %s and value %s' % (sub_key, value))
    return get_key_value_data(winreg.HKEY_CLASSES_ROOT, sub_key, value)

def get_hkcu_key_value_data(sub_key, value):
    """ Return the data stored under the fiven sub_key and value in the root 
        HKEY_CURRENT_USER.
    """
    WriteDebug('get_hkcu_key_value_data() called for sub_key %s and value %s' % (sub_key, value))
    return get_key_value_data(winreg.HKEY_CURRENT_USER, sub_key, value)

@AccessDeniedHandler
def get_key_value_data(root_key, sub_key, value):
    """ Return the data under the given value of a sub_key under a root_key. """

    WriteDebug('get_key_value_data() called.')
    WriteDebug('sub_key: %s, value: %s' % (sub_key, value))

    root_key = _as_unicode(root_key)
    sub_key = _as_unicode(sub_key)
    value = _as_unicode(value)

    access_denied = False
    return_value = None

    try:
        WriteDebug('Opening the sub_key.')
        key = winreg.OpenKey(root_key, sub_key, 0, 
                             winreg.KEY_QUERY_VALUE | winreg.KEY_WOW64_64KEY)
        WriteDebug('sub_key opened, quering value.')

        try:
            results = winreg.QueryValueEx(key, value)
    
            # results should be tuple of two items.
            if not type(results) is tuple or len(results) != 2:
                WriteDebug('Something failed in the call, returning None')
            else:
                # The string is in the first item of the tuple.
                return_value = results[0]
        except WindowsError as  wE:
            WriteDebug('Failed (Windows error) calling to QueryValueEx: %s' % wE.strerror)
            access_denied = wE.winerror == ERROR_ACCESS_DENIED
        finally:
            winreg.CloseKey(key)

    except WindowsError as  wE:
        WriteDebug('Failed (Windows error) calling to OpenKey: %s' % wE.strerror)
        access_denied = wE.errno == ERROR_ACCESS_DENIED
    except Exception as eX:
        WriteDebug('Failed in get_key_value_data: %s' % eX)
        access_denied = False

    WriteDebug('return_value is: %s' % return_value)
    return access_denied, return_value