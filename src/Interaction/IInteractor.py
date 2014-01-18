from Interaction import InteractionTypes

class IInteractor(object):
    """ Interface that define the interaction between the flow code, and the ui. 
        UI can be anything from Console to Window.
    """

    InteractionType = InteractionTypes.NotSet
    IS_LOADED       = False

    def __init__(self):
        """ def:    Constructor for the IInteract. by default, we only set 
                    the InteractionType.
            input:  None.
            return: None.
        """
        IInteractor.InteractionType = InteractionTypes.NotSet
    def load(self):
        """ def:    Final stage before using the interactor. notifyLoaded 
                    should be called in here.
            input:  None.
            return: None.
        """
        raise NotImplementedError('IInteractor.load')

    def notifyLoaded(self):
        """ def:    Function to notify that the interactor is loaded.
            input:  None.
            return: None.
        """
        raise NotImplementedError('IInteractor.notifyLoaded') 

    @staticmethod
    def IsLoaded():
        """ def:    Static function to check if the interactor is fully loaded 
                    (for other thread to start interact with it).
            input:  None.
            return: Boolean, True if loaded, otherwise False.
        """
        raise NotImplementedError('IInteractor.IsLoaded') 

    def writeLog(self, logMsg):
        """ def:    Function to print a log message to the user. Messages will 
                    pass at the same format of the Logs class, 
                    ie: <logType>__||__<message>. parsing will be made in here.
            input:  logMsg - the message to print.
            return: None.
        """
        raise NotImplementedError('IInteractor.writeLog')

    def getSearchInput(self, logMsg = None):
        """ def:    Function to get the user input from the search box.    
            input:  default - None, optional - logMsg (will call writeLog).
            return: str containing the user input.
        """
        raise NotImplementedError('IInteractor.getSearchInput')

    def getDestinationDirectoryInput(self, default_directory, logMsg = None):
        """ def:    Function to get the user input from the destination 
                    directory box.
            input:  default_directory - directory to place by default in the 
                    input 
                    optional - logMsg (will call writeLog).
            return: str containing the user input.
        """
        raise NotImplementedError('IInteractor.getDestinationDirectoryInput')
    
    def getMovieChoice(self, subMovies, logMsg = None):
        """ def:    Function to get the user choice from the movies list view.
            input:  list of SubMovie, optional - logMsg (will call writeLog).
            return: the selected SubMovie.
        """
        raise NotImplementedError('IInteractor.getMovieChoice')

    def getVersionChoice(self, subVersions, subMovies, logMsg = None):
        """ def:    Function to get the user choice from the versions list view. 
                    Notice that we might allow the user to selected another 
                    movie in the lower levels of the call stack.
            input:  list of SubVersion. list of SubMovies.
                    optional - logMsg (will call writeLog).
            return: the selected SubVersion/SubMovie
        """
        raise NotImplementedError('IInteractor.getVersionChoice')

    def notifyNewVersion(self, current_version, new_version, new_version_link):
        """ def:    Function to notify the user that there's new version of 
                    SubiT.
            input:  current_version - SubiT's current version
                    new_version - SubiT's latest_version
                    new_version_link - http link to the latest version page
            return: None
        """
        raise NotImplementedError('IInteractor.notifyNewVersion')

