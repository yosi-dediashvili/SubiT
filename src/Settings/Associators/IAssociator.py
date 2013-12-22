class IAssociator(object):
    """ Interface for Associators. Associator is an class that associates SubiT
        under a certain file extensions. A given Associator is relvant only for 
        a certain Platform, ie: Windows\Linux. The class will add SubiT 
        to the right-click menu for the extensions given in the configuration 
        file. The relevant Associator will be chosen by the Associators module
        according to the system platform, and will be retrieved using the
        getAssociator() function in the module.

        Ideally, the associator should use the extensions under the configuration,
        but there might be exceptions to that rule. ie: .desktop format under 
        linux requires a file format, and not extension.
    """
    # The text that will apear in the
    MENU_TEXT           = 'SubiT'
    # Params for program
    ASSOCIATE_COMMAND   = '-associate'
    UNASSOCIATE_COMMAND = '-unassociate'


    @classmethod
    def GetRelevantPlatform(cls):
        """ The platform relevant for this associator. The value should be 
            identical to the result of Utils.GetSystemPlatform() under the 
            relevant platform, otherwise, the Associator won't be chosen by 
            the Associators module.
        """
        raise NotImplementedError('IAssociator.GetRelevantPlatform')
    @classmethod
    def SetAssociation(cls):
        """ Set the association for the relevant extensions.
            Return True if succeeded, else False. """
        raise NotImplementedError('IAssociator.SetAssociation')
    @classmethod
    def RemoveAssociation(cls):
        """ Remove the association for the relevant extensions.
            Return True if succeeded, else False. """
        raise NotImplementedError('IAssociator.RemoveAssociation')