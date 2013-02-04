from Settings.Associators.WinAssociator import WinAssociatorHelper
from Utils import GetMoviesExtensions
from Utils import WriteDebug

# The GUID for subit's COM dll.
SUBIT_GUID = '{F61F4CF8-108A-4642-BB20-1F09A38C4AA5}'
# The class type for the Shell extension.
SUBIT_REG_CLASS_NAME = 'SubiT.ShellExt'
# Path of subit under some extension in the registry.
SUBIT_REG_PATH_EXT = 'shellex\\ContextMenuHandlers\\' + SUBIT_REG_CLASS_NAME

def SetCurrentAssociationCommand(command):
    """ The function should be called when ever the association command should
        be changed if we face an ACCESS_DENIED error.
    """
    WinAssociatorHelper.InitCurrentAssociationCommand(command)

def IsContextMenuHandlerEqualsToOurPath():
    """ Check if the ContextMenuHandler that is registered for SubiT is 
        refering to our Dll path, or some other path.
    """
    sub_key = 'CLSID\\%s\\InprocServer32' % SUBIT_GUID
    # We query for the (default value) value
    value = None

    WriteDebug('Getting the dll path under SubiT\'s ContextMenuHandler.')
    reg_dll_path = WinAssociatorHelper.get_hkcr_key_value_data(sub_key, value)
    WriteDebug('The Dll path is: %s' % reg_dll_path)
    WriteDebug('The real path to our Dll is: %s' % WinAssociatorHelper.CONTEXT_MENU_HANDLER_FULL_PATH)

    return reg_dll_path == WinAssociatorHelper.CONTEXT_MENU_HANDLER_FULL_PATH

def IsSubiTContextMenuHandlerRegistered():
    """ Check if the ContextMenuHandler is registered. """
    WriteDebug('IsSubiTContextMenuHandlerRegistered() called.')
    registered = WinAssociatorHelper.is_clsid_registered_in_hkcr(SUBIT_GUID)
    WriteDebug('IsSubiTContextMenuHandlerRegistered? %s' % registered)
    return registered

def RegisterSubiTContextMenuHandler():
    """ Register the ContextMenuHandler. """
    WriteDebug('RegisterSubiTContextMenuHandler() called.')

    sub_key = 'CLSID\\%s' % SUBIT_GUID

    WriteDebug('Creating the root key at %s' % sub_key)
    succeeded = WinAssociatorHelper.set_hkcr_registry_key_and_value\
        (sub_key, None, SUBIT_REG_CLASS_NAME)

    WriteDebug('succeeded: %s' % succeeded)
    
    # Keep in mind the we might called ourself elevated, and we actually did
    # succeeded in the registration, but we can't realy know that right now...
    if not succeeded:
        WriteDebug('The current session failed creating the root key, returning False.')
        return False

    sub_key += '\\InprocServer32'
    dll_path = WinAssociatorHelper.CONTEXT_MENU_HANDLER_FULL_PATH

    WriteDebug('Setting the path to the dll to: %s' % dll_path)
    succeeded = WinAssociatorHelper.set_hkcr_registry_key_and_value\
        (sub_key, None, dll_path)
    WriteDebug('succeeded: %s' % succeeded)

    if not succeeded:
        WriteDebug('The current session failed setting the Dll path, returning False.')
        return False

    WriteDebug('Setting the ThreadingModel.')
    succeeded = WinAssociatorHelper.set_hkcr_registry_key_and_value\
        (sub_key, 'ThreadingModel', 'Apartment')
    WriteDebug('succeeded: %s' % succeeded)

    if not succeeded:
        WriteDebug('The current session failed setting the ThreadingModel, returning False.')
        return False

    return True

def UnregsiterSubiTContextMenuHandler():
    """ Unregister the ContextMenuHandler. """
    WriteDebug('UnregsiterSubiTContextMenuHandler() called.')

    sub_key = 'CLSID\\%s' % SUBIT_GUID

    WriteDebug('Removing the root key: %s' % sub_key)
    succeeded = WinAssociatorHelper.delete_hkcr_registry_key_tree(sub_key)

    WriteDebug('succeeded: %s' % succeeded)

    if succeeded:
        WriteDebug('The root_key deleted.')
    else:
        WriteDebug('The current session failed deleting the root_key.')

    return succeeded

def GetExtensionsForAssociation():
    """ Get a list of all the extesions we need to associate with. """
    return GetMoviesExtensions();

def _isTheOldSubiTContextMenuIsAssociatedWithExtension(file_extension):
    """ Check if the old context menu of SubiT apears under the given file 
        extension.
    """
    WriteDebug('_isTheOldSubiTContextMenuIsAssociatedWithExtension(%s) called.' % file_extension)

    ext_key = WinAssociatorHelper\
        .get_relevant_key_handle_for_extension_association(file_extension)

    if ext_key is None:
        WriteDebug('The current session failed getting the relevant key, returning False.')
        return False
    
    WriteDebug('The key retrieved.')    
    key_exists = WinAssociatorHelper.is_key_exists\
        (ext_key, 'shell\\SubiT', True)

    WriteDebug('key_exists: %s' % key_exists)
    if key_exists is None:
        WriteDebug('The current session failed when trying to check if SubiT is registered under the extension, returning False.')
        return False

    return key_exists

    

def _disassociateTheOldSubiTContextMenuWithExtensions(file_extension):
    """ Remove the association of the old context menu from the given file
        extension.
    """
    WriteDebug('_disassociateTheOldSubiTContextMenuWithExtensions(%s) called.' % file_extension)

    ext_key = WinAssociatorHelper\
        .get_relevant_key_handle_for_extension_association(file_extension)

    if ext_key is None:
        WriteDebug('The current session failed getting the relevant key, returning False.')
        return False
    
    WriteDebug('The key retrieved.')
    deleted = WinAssociatorHelper.delete_registry_key_tree\
        (ext_key, 'shell\\SubiT', True)

    WriteDebug('deleted: %s' % deleted)
    if deleted is None:
        WriteDebug('The current session failed deleting old SubiT, returning False.')
        return False

    return deleted

def IsSubiTContextMenuHandlerAssociatedWithExtension(file_extension):
    """ Check if the ContextMenuHandler is associated with that extension. """
    WriteDebug('IsSubiTContextMenuHandlerAssociatedWithExtension(%s) called.' % file_extension) 

    ext_key = WinAssociatorHelper\
        .get_relevant_key_handle_for_extension_association(file_extension)

    if ext_key is None:
        WriteDebug('The current session failed getting the relevant key, returning False.')
        return False
    
    if WinAssociatorHelper.is_key_exists(ext_key, SUBIT_REG_PATH_EXT):
        WriteDebug('The key exists.')
        guid_value = WinAssociatorHelper.get_key_value_data\
            (ext_key, SUBIT_REG_PATH_EXT, None)
        if guid_value == SUBIT_GUID:
            WriteDebug('The guid are equals, we are registered.')
            return True

    WriteDebug('We are not registered.')
    return False

def AssociateSubiTContextMenuHandlerWithExtension(file_extension):
    """ Associate the ContextMenuHandler with a single file extension. """
    WriteDebug('AssociateSubiTContextMenuHandlerWithExtension(%s) called.' % file_extension)

    if IsSubiTContextMenuHandlerAssociatedWithExtension(file_extension):
        WriteDebug('file_extension is already associcated.')
        return False

    if _isTheOldSubiTContextMenuIsAssociatedWithExtension(file_extension):
        _disassociateTheOldSubiTContextMenuWithExtensions(file_extension)

    ext_key = WinAssociatorHelper\
        .get_relevant_key_handle_for_extension_association(file_extension)

    if ext_key is None:
        WriteDebug('The current session failed getting the relevant key, returning False.')
        return False

    succeeded = WinAssociatorHelper.set_registry_key_and_value\
        (ext_key, SUBIT_REG_PATH_EXT, None, SUBIT_GUID)

    if succeeded:
        WriteDebug('ContextMenuHandler successfully registered for the extension.')
    else:
        WriteDebug('ContextMenuHandler failed in regsitration for the extension.')

    return succeeded

def DisassociateSubiTContextMenuHandlerWithExtension(file_extension):
    """ Disassociate the ContextMenuHandler from a single file extension. """
    WriteDebug('DisassociateSubiTContextMenuHandlerWithExtension(%s) called.' % file_extension)
    if not IsSubiTContextMenuHandlerAssociatedWithExtension(file_extension):
        WriteDebug('file_extension is not associcated.')
        return True

    ext_key = WinAssociatorHelper\
        .get_relevant_key_handle_for_extension_association(file_extension)

    if ext_key is None:
        WriteDebug('The current session failed getting the relevant key, returning False.')
        return False

    succeeded = WinAssociatorHelper.delete_registry_key_tree\
        (ext_key, SUBIT_REG_PATH_EXT, True)

    if succeeded:
        WriteDebug('ContextMenuHandler successfully unregistered for the extension.')
    else:
        WriteDebug('ContextMenuHandler failed in unregsitration for the extension.')

    return succeeded
