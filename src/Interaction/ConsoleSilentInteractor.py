import os

from Interaction import IInteractor
from Interaction import InteractionTypes

from Logs import MessageString
from Logs import MessageType

class ConsoleSilentInteractor(IInteractor.IInteractor):
    """ Silent Console implementation of the IInteractor. Serves SubiT in the 
        console mode where we dont want to ask the user for chosice, but simply
        write the logs to the console. We implement the silent feature by using
        the pass keyword in the interation functions (those that starts with 
        the "get", i.e. getSearchInput and so on.
    """
    IS_LOADED = False

    def __init__(self):
        super(ConsoleSilentInteractor, self).__init__()
        ConsoleSilentInteractor.InteractionType = \
            InteractionTypes.ConsoleSilent

    def notifyLoaded(self):
        ConsoleSilentInteractor.IS_LOADED = True

    def load(self):
        self.notifyLoaded()

    @staticmethod
    def IsLoaded():
        return ConsoleSilentInteractor.IS_LOADED

    def writeLog(self, logMsg):
        type_message = MessageType(logMsg)
        real_message = MessageString(logMsg)

        print('[%s] - %s' % (type_message, real_message))

    def getSearchInput(self, logMsg = None):
        pass

    def getDestinationDirectoryInput(self, default_directory, logMsg = None):
        pass

    def getMovieChoice(self, subMovies, logMsg = None):
        pass

    def getVersionChoice(self, subVersions, subMovies, logMsg = None):
        pass

    def notifyNewVersion(self, current_version, new_version, new_version_link):
        message = ('====================================================\r\n'
                   'New version of SubiT is available!              \r\n'
                   'Your version is: %s, latest version is: %s. \r\n\r\n'
                   'The latest version is avaliable at: %s          \r\n'
                   '====================================================\r\n' 
                   % (current_version, new_version, new_version_link))
        input(message)


