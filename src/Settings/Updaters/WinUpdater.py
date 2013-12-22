import os
import sys

from Settings.Updaters import IUpdater
from Utils import GetProgramDir, GetProgramDir

class WinUpdater(IUpdater.IUpdater):
    """ Implementation of IUpdater for Windows platform """

    LATEST_VERSION_PAGE = \
        r'http://subit-app.sourceforge.net/updates/win_latest_version.html'
    UPDATE_FILE_LOCATION = os.path.join\
        (GetProgramDir(), 'Settings\\Updaters\\Update_Files')

    @classmethod
    def GetRelevantPlatform(cls):
        return 'Windows'

    @classmethod
    def DownloadUpdate(cls, url_to_download, latest_version):
        from urllib import urlretrieve

        from Utils import WriteDebug
        from Settings.Updaters.UpdaterExceptions import \
            DownloadUpdaterException, DownloadUrlMissingUpdaterException

        try:
            if not url_to_download:
                raise DownloadUpdaterException('url_to_download is empty!')
            if not latest_version:
                raise DownloadUpdaterException('latest_version is empty!')
            if not cls.UPDATE_FILE_LOCATION:
                raise DownloadUpdaterException('UPDATE_FILE_LOCATION is empty!')
                
            WriteDebug('Going to download the latest version')
            _file_name = cls.FromVersionToUpdateFileName(latest_version)
            WriteDebug('_file_name: %s' % _file_name)
            _full_path = os.path.join(cls.UPDATE_FILE_LOCATION, _file_name)
            WriteDebug('_full_path: %s' % _full_path)
            # urlretrieve will raise exception if the directory is 
            # missing so we need to check this before, and create the 
            # directory
            if not os.path.exists(cls.UPDATE_FILE_LOCATION):
                WriteDebug('Update_Files directory is missing, creating it!')
                os.mkdir(cls.UPDATE_FILE_LOCATION)

            try:
                WriteDebug('Trying to download: %s' % url_to_download)
                urlretrieve(url_to_download, _full_path)
            except:
                raise DownloadUpdaterException\
                    ('Failed retriving: %s' % url_to_download)

            WriteDebug('Update downloaded: %s' % _full_path)
            return True

        except Exception as eX:
            WriteDebug('Failed downloading the latest version: %s' % eX)
            return False

    @classmethod
    def UpdateFileIsWaitingInDirectory(cls):
        from Utils import WriteDebug, myfilter

        WriteDebug('UPDATE_FILE_LOCATION is %s' % cls.UPDATE_FILE_LOCATION)
        if not os.path.exists(cls.UPDATE_FILE_LOCATION):
            # If the directory doesnt exists, there's no need for us to do 
            # further checks, because if there was a new update waiting, the
            # directory whould have existed
            WriteDebug('Update directory doesnt exists, skipping check')
            return (False, None)

        WriteDebug('Update directory exists, checking for file names...')
        
        _current_version = cls.CurrentVersion()
        # Get the versions of all the update files
        _update_files_vers = myfilter\
            (cls.IsUpdateFileName, os.listdir(cls.UPDATE_FILE_LOCATION), 
             cls.FromUpdateFileNameToVersion)
        WriteDebug('Our current version is: %s' % _current_version)
        WriteDebug('Update files in versions are: %s' % _update_files_vers)
        # We Take the first file that is newer than our version
        for _update_file_ver in _update_files_vers:                                        
            if cls.IsNewerVersion(_current_version, _update_file_ver):
                WriteDebug('Found new version: %s' % _update_file_ver)
                _file_name = cls.FromVersionToUpdateFileName(_update_file_ver)
                _update_file_path = os.path.join\
                    (cls.UPDATE_FILE_LOCATION, _file_name)
                return (True, _update_file_path)

        WriteDebug('There is no new version waiting')
        return (False, None)

    @classmethod
    def ApplyUpdate(cls, update_file_path):
        from Utils import WriteDebug
        from Settings.Updaters.UpdaterExceptions import ApplyUpdaterException

        updater_path = os.path.join\
            (GetProgramDir(), 'Settings', 'Updaters', 'SubiT-updater.exe')
        if not os.path.exists(updater_path):
            WriteDebug('updater_path is missing: %s' % updater_path)
            raise ApplyUpdaterException('updater is missing')

        args = sys.argv
        args[0] = updater_path
        args.insert(1, update_file_path)
        WriteDebug('Calling os.execv for the updater with args: %s' % args)
        os.execv(updater_path, args)