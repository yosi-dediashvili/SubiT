import os
from Settings.Updaters import IUpdater

class LinuxUpdater(IUpdater.IUpdater):
    """ Implementation of IUpdater for Linux platform. Currently, we support
        only notification of new version, without auto-update features. """

    LATEST_VERSION_PAGE = \
        r'http://subit-app.sourceforge.net/updates/lnx_latest_version.html'
    
    @classmethod
    def GetRelevantPlatform(cls):
        return 'Linux'

    @classmethod
    def ShouldAutoUpdate(cls):
        return False

    @classmethod
    def UpdateFileIsWaitingInDirectory(cls):
        return False