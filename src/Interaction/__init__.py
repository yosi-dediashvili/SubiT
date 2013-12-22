from Settings.Config import SubiTConfig

class InteractionTypes:
        """ We need to know the type of interactor in some cases (getting the 
            settings gui and so...)
        """
        NotSet        = -1 # Default for IInteract
        Gui           = 0  # Gui interaction
        GuiSilent     = 1  # Gui silent mode
        Console       = 2  # Console interaction
        ConsoleSilent = 3  # Console silent mode

Interactor = None

def setDefaultInteractorByConfig():
    """ Will set the interactor defined in the config. Raises ImportError when
        the interaction_type that is set in the config is not one of the types
        in the enum IInteractor.InteractionTypes.
    """
    interaction_type = getDefaultInteractorByConfig()

    if interaction_type == InteractionTypes.Gui:
        from Interaction.GuiInteractor import GuiInteractor
        setInteractor(GuiInteractor())
    elif interaction_type == InteractionTypes.GuiSilent:
        raise NotImplementedError('GuiSilentInteractor is not written yet!')
    elif interaction_type == InteractionTypes.Console:
        from Interaction.ConsoleInteractor import ConsoleInteractor
        setInteractor(ConsoleInteractor())
    elif interaction_type == InteractionTypes.ConsoleSilent:
        from Interaction.ConsoleSilentInteractor import ConsoleSilentInteractor
        setInteractor(ConsoleSilentInteractor())
    else:
        raise ImportError('No Interactor for type: %s' % interaction_type)
   
def getDefaultInteractorByConfig():
    """ Will return the type of the interactor that is set in the config. The
        return value is an integer, and should be compared to the enum of the
        InteractionTypes. On failure, the function will return NotSet as the 
        default interactor.
    """
    return SubiTConfig.Singleton().getInt\
        ('Global', 'interaction_type', InteractionTypes.NotSet)

def setInteractor(interactor):
    """ Function to set the instance of the interactor. The interactor must be 
        an instance of IInteractor implementation (is passed after calling his 
        constuctor). 
    """
    global Interactor
    Interactor = interactor

def getInteractor():
    """ Function to get the instance of the interactor. """
    global Interactor
    return Interactor