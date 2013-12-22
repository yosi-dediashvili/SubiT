from Settings.Associators.IAssociator import IAssociator
from Settings.Associators.WinAssociator import WinAssociatorExtension

class WinAssociator(IAssociator):
    """ Associator for Windows platform. Association is made via Registry. 
        The associator for windows is combined with a ContextMenuHandler dll
        written for the program. 
    """

    @classmethod
    def GetRelevantPlatform(cls):
        return 'Windows'
        
    @classmethod
    def SetAssociation(cls):
        from Settings.Associators import ASSOCIATE_COMMAND
        WinAssociatorExtension.SetCurrentAssociationCommand(ASSOCIATE_COMMAND)

        handler_registered = True

        if (not WinAssociatorExtension.IsSubiTContextMenuHandlerRegistered() or
            not WinAssociatorExtension.IsContextMenuHandlerEqualsToOurPath()):
            handler_registered =  \
                WinAssociatorExtension.RegisterSubiTContextMenuHandler()

        if handler_registered:
            for file_ext in WinAssociatorExtension.GetExtensionsForAssociation():
                WinAssociatorExtension.\
                    AssociateSubiTContextMenuHandlerWithExtension(file_ext)
        

    @classmethod
    def RemoveAssociation(cls):
        from Settings.Associators import DISASSOCIATE_COMMAND
        WinAssociatorExtension.SetCurrentAssociationCommand(DISASSOCIATE_COMMAND)

        handler_unregistered = True

        if WinAssociatorExtension.IsSubiTContextMenuHandlerRegistered():
            handler_unregistered = \
                WinAssociatorExtension.UnregsiterSubiTContextMenuHandler()

        if handler_unregistered:
            for file_ext in WinAssociatorExtension.GetExtensionsForAssociation():
                WinAssociatorExtension.\
                    DisassociateSubiTContextMenuHandlerWithExtension(file_ext)