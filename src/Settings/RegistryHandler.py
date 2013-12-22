import _winreg
import ctypes
from ctypes import byref, wintypes
import os
import Utils



#=======================================================================
# Predefined CONST and Function taken from windows lib
#=======================================================================
ASSOCF_INIT_IGNOREUNKNOWN	= 0x00000400 
ASSOCKEY_CLASS 				= 3


REG_SZ 						= _winreg.REG_SZ
REG_EXPAND_SZ               = _winreg.REG_EXPAND_SZ

ERROR_SUCCESS               = 0x0
ERROR_ACCESS_DENIED         = 0x5
ERROR_PATH_NOT_FOUND        = 0x2

KEY_READ    = 0x20019
KEY_WRITE   = 0x20006


#Win32 api Functions. We use unicode functions (same as python's)
SHDeleteKey     = None
RegDeleteTree   = None
AssocQueryKey   = None
RegCloseKey     = None
RegOpenKeyEx    = None
RegCreateKeyEx  = None
RegSetValueEx   = None
RegSetValue     = None

#Try to import only if we're under windows
if Utils.IsWindowPlatform():
	if Utils.IsVistaOrLater():
		RegDeleteTree = ctypes.windll.advapi32.RegDeleteTreeW
	else:
		SHDeleteKey 	= ctypes.windll.shlwapi.SHDeleteKeyW

	AssocQueryKey 	= ctypes.windll.shlwapi.AssocQueryKeyW
	RegCloseKey 	= ctypes.windll.advapi32.RegCloseKey
	#LONG WINAPI RegOpenKeyEx(
	#  __in        HKEY hKey,
	#  __in_opt    LPCTSTR lpSubKey,
	#  __reserved  DWORD ulOptions,
	#  __in        REGSAM samDesired,
	#  __out       PHKEY phkResult
	#);
	RegOpenKeyEx    = ctypes.windll.advapi32.RegOpenKeyExW
	#LONG WINAPI RegCreateKeyEx(
	#  __in        HKEY hKey,
	#  __in        LPCTSTR lpSubKey,
	#  __reserved  DWORD Reserved,
	#  __in_opt    LPTSTR lpClass,
	#  __in        DWORD dwOptions,
	#  __in        REGSAM samDesired,
	#  __in_opt    LPSECURITY_ATTRIBUTES lpSecurityAttributes,
	#  __out       PHKEY phkResult,
	#  __out_opt   LPDWORD lpdwDisposition
	#);
	RegCreateKeyEx  = ctypes.windll.advapi32.RegCreateKeyExW
	RegSetValueEx   = ctypes.windll.advapi32.RegSetValueExW
	RegSetValue     = ctypes.windll.advapi32.RegSetValueW
#=======================================================================
#=======================================================================

def getRelevantKey( ext ):
	"""Function to retrieve handle to the relevant key for the specific ext"""
	hKey = wintypes.HKEY()
	error_code = AssocQueryKey( ASSOCF_INIT_IGNOREUNKNOWN,
								ASSOCKEY_CLASS,
								unicode(ext),
								0,
								byref(hKey))
	Utils.WriteDebug('AssocQueryKey error_code: %s' % error_code)
	return (error_code, hKey)

def isSubiTRegistered(ext):
	"""Function to check if we're registered on the given extension"""	
	result = False
	(error_code, hKey) = getRelevantKey(ext)
	subitKey = wintypes.HKEY()
	if error_code == ERROR_SUCCESS:
		open_error_code = RegOpenKeyEx( hKey, u'shell\\SubiT', 0, 
										KEY_READ, byref(subitKey))
		Utils.WriteDebug('RegOpenKeyEx error_code: %s' % open_error_code)
		result = (open_error_code == ERROR_SUCCESS)
	
	RegCloseKey(subitKey)
	RegCloseKey(hKey)
	return result
	

#=======================================================================
#
#=======================================================================	
def register( hKey, progPath ):
	"""Function to register the given extension on the registry, using the path given to the SubiT.exe file."""
	import Gui
	reg_defaule_value_value = '"%s" "%%1"' % progPath
	reg_icon_value          = os.path.join(Gui.IMAGES_LOCATION, 'icon.ico')
	subitHKey               = wintypes.HKEY()
	return_code             = 0x00000000

	#Open/Create SubiT's key
	retCode = RegCreateKeyEx(   hKey, u'shell\SubiT', 0, 0, 0x00000000L, #REG_OPTION_NON_VOLATILE
								KEY_WRITE, 0, byref(subitHKey), 0)
	#If we succeeded to gain access
	if retCode == ERROR_SUCCESS:
		#Register the default value for SubiT key
		reg_default_value_err_code = RegSetValue(   subitHKey, u'command', #commnad's "defaule value" value
													REG_SZ, unicode(reg_defaule_value_value), 0)
		#Set the icon for SubiT's key
		reg_icon_err_code = RegSetValueEx(subitHKey, u'Icon', #"defaule value" value
										0, REG_SZ, unicode(reg_icon_value), 
										#Unicode length is 2 Bytes per char, we need string length + the null terminate char (we use +2 for that)
										len(unicode(reg_icon_value)) * 2 + 2)

		return_code = reg_default_value_err_code | reg_icon_err_code
	
	RegCloseKey(subitHKey)
	RegCloseKey(hKey)
	Utils.WriteDebug('register->error_code for RegSetValue/RegSetValueEx: %s' % return_code)
	#Return bitwise oR for of both registration
	return return_code

def unregister( hKey ):
	error_code  = ERROR_SUCCESS
	subitHKey   = wintypes.HKEY()
	#Open/Create SubiT's key
	error_code = RegOpenKeyEx(  hKey, u'shell\SubiT', 0, 
								KEY_WRITE, byref(subitHKey))
	#If we succeeded to gain access
	if error_code == ERROR_SUCCESS:
		if Utils.IsVistaOrLater():
			error_code = RegDeleteTree(hKey, u'shell\\SubiT')
		elif Utils.IsWindowPlatform():
			error_code = SHDeleteKey(hKey, u'shell\\SubiT')

	RegCloseKey(hKey)
	RegCloseKey(subitHKey)
	Utils.WriteDebug('unregister->error_code for RegDeleteTree/SHDeleteKey: %s' % error_code)
	return error_code