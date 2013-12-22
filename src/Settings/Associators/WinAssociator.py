from Settings.Associators.IAssociator import IAssociator
from Settings.Associators import WinAssociatorHelper

class WinAssociator(IAssociator):
    """ Associator for Windows platform. Association is made via Registry. """

    @classmethod
    def GetRelevantPlatform(cls):
        return 'Windows'
        
    @classmethod
    def SetAssociation(cls):
        WinAssociatorHelper.SetSubitPath(cls.MENU_TEXT)
        return WinAssociatorHelper.register_all(cls.ASSOCIATE_COMMAND)

    @classmethod
    def RemoveAssociation(cls):
        WinAssociatorHelper.SetSubitPath(cls.MENU_TEXT)
        return WinAssociatorHelper.unregister_all(cls.UNASSOCIATE_COMMAND)