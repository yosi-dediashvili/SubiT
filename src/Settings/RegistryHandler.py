import _winreg
import ctypes
from ctypes import byref, wintypes



#=======================================================================
# Predefined CONST and Function taken from windows lib
#=======================================================================
ASSOCF_INIT_IGNOREUNKNOWN	= 0x00000400 
ASSOCKEY_CLASS 				= 3
REG_SZ 						= _winreg.REG_SZ

AssocQueryKey 	= ctypes.windll.Shlwapi.AssocQueryKeyW
SHDeleteKey 	= ctypes.windll.Shlwapi.SHDeleteKeyW
RegCloseKey 	= ctypes.windll.Advapi32.RegCloseKey
#=======================================================================
#=======================================================================

#=======================================================================
#Function to retrieve handle to the relevant key for the specific ext.
#=======================================================================
def getRelevantKey( ext ):
	hKey = wintypes.HKEY()
	val = AssocQueryKey(ASSOCF_INIT_IGNOREUNKNOWN,
						ASSOCKEY_CLASS,
						unicode(ext),
						0,
						byref(hKey))
	return (val, hKey)

#=======================================================================
#Function to register the given extension on the registry, using the 
#path given to the SubiT.exe file.
#=======================================================================	
def register( hKey, progPath ):
	with _winreg.CreateKeyEx(hKey.value, u'shell\\SubiT\\command') as setKey:
		regvalue = u'"%s" "%%1"' % progPath
		_winreg.SetValueEx(setKey, None, 0, REG_SZ, regvalue)
		RegCloseKey(hKey)
	
def unregister( hKey ):
	ret = SHDeleteKey(hKey, u'shell\\SubiT')
	return not bool(ret)