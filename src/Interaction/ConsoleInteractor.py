import os

from Interaction import IInteractor
from Interaction import InteractionTypes

from Logs import MessageString
from Logs import MessageType

class ConsoleInteractor(IInteractor.IInteractor):
    """Console implementation of the IInteractor. Serves SubiT in the console mode."""
    IS_LOADED = False


    def __init__(self):
        super(ConsoleInteractor, self).__init__()
        ConsoleInteractor.InteractionType = InteractionTypes.Console

    def notifyLoaded(self):
        ConsoleInteractor.IS_LOADED = True

    def load(self):
        self.notifyLoaded()

    @staticmethod
    def IsLoaded():
        return ConsoleInteractor.IS_LOADED

    def writeLog(self, logMsg):
        type_message = MessageType(logMsg)
        real_message = MessageString(logMsg)

        print('[%s] - %s' % (type_message, real_message))

    def getSearchInput(self, logMsg = None):
        if logMsg:
            self.writeLog(logMsg)
        return_value = None
        while not return_value:
            return_value = raw_input()
        return return_value

    def getDestinationDirectoryInput(self, default_directory, logMsg = None):
        if logMsg:
            self.writeLog(logMsg)
        dest = None
        def _isValidInput(_input):
            if not os.path.exists(_input):
                print('Path does not exists')
                return False
            return True
        dest = raw_input('Leave empty for [%s]: ' % default_directory)
        # If the user simply pressed enter, we'll set the suggested directory
        dest = dest if dest else default_directory
        while not _isValidInput(dest):
            dest = raw_input('Leave empty for [%s]: ' % default_directory)
            dest = dest if dest else default_directory
        return dest

    def getMovieChoice(self, subMovies, logMsg = None):
        if logMsg:
            self.writeLog(logMsg)

        total_items = range(1, len(subMovies))
        for i in total_items:
            print('%s. %s' % (i,subMovies[i].movie_name + 
                              (' -> ' + subMovies[i].versions_sum if subMovies[i].versions_sum else '')))
        print('Enter the index of the desired movie: ')
        index_value = None
        def _isValidInput(_input):
            if not _input.isdigit():
                print('Value must be a int')
                return False
            elif not int(_input) in total_items:
                print('Value must be between %s and %s' % (min(total_items), max(total_items)))
                return False
            else:
                return True

        index_value = raw_input()
        while not _isValidInput(index_value):
            index_value = raw_input()
        return subMovies[int(index_value)]

    def getVersionChoice(self, subVersions, subMovies, logMsg = None):
        if logMsg:
            self.writeLog(logMsg)

        if subVersions:
            def _isValidInput(_input, _total_items):
                if not _input.isdigit():
                    print('Value must be a int')
                    return False
                elif not int(_input) in _total_items:
                    print('Value must be between %s and %s' % (min(_total_items), max(_total_items)))
                    return False
                else:
                    return True
            total_items = range(1, len(subVersions))
            for i in total_items:
                print('%s. %s' % (i, subVersions[i].version_sum))
            print('Enter the index of the desired version: ')
            index_value = None
            index_value = raw_input()
            while not _isValidInput(index_value, total_items):
                index_value = raw_input()
            return subVersions[int(index_value)]
        # we choose submovies
        else:
            return self.getMovieChoice(subMovies)

    def notifyNewVersion(self, current_version, new_version, new_version_link):
        message = ('====================================================\r\n'
                   'New version of SubiT is available!              \r\n'
                   'Your version is: %s, latest version is: %s. \r\n\r\n'
                   'The latest version is avaliable at: %s          \r\n'
                   '====================================================\r\n' 
                   % (current_version, new_version, new_version_link))
        input(message)


