import _winreg
import ctypes
from ctypes import byref, wintypes
import os



#=======================================================================
# Predefined CONST and Function taken from windows lib
#=======================================================================
ASSOCF_INIT_IGNOREUNKNOWN	= 0x00000400 
ASSOCKEY_CLASS 				= 3
REG_SZ 						= _winreg.REG_SZ
REG_EXPAND_SZ               = _winreg.REG_EXPAND_SZ

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
    import Gui
    with _winreg.CreateKeyEx(hKey.value, 'shell\\SubiT') as subitKey:
        _winreg.SetValueEx(subitKey, 'Icon', 0, REG_EXPAND_SZ, os.path.join(Gui.IMAGES_LOCATION, 'icon.ico'))
        with _winreg.CreateKeyEx(subitKey, 'command') as cmdKey:
            regvalue = '"%s" "%%1"' % progPath
            _winreg.SetValueEx(cmdKey, None, 0, REG_SZ, regvalue)
        RegCloseKey(hKey)

def unregister( hKey ):
	ret = SHDeleteKey(hKey, 'shell\\SubiT')
	return not bool(ret)