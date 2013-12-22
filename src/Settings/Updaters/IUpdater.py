class IUpdater(object):
    """ Abstract class for SubiT update procedures. A full implementation 
        should be made for each platform (because different files should be 
        downloaded and placed in different folders). A partial implementation 
        can also be made for a platform, i.e. allowing to check for update but 
        not to apply the auto-update feature.
    """
    # Check every 12 hours
    TIME_BETWEEN_CHECKS = 60 * 60 * 12 
    SUBIT_DOMAIN        = r'www.subit-app.sourceforge.net'
    # Link to the latest version page of the relevant platform. 
    LATEST_VERSION_PAGE = None
    # Link to the latest version download page of the relevant platform
    LATEST_VERSION_DOWN = None
    # The local path without the file name in which the update file should be
    UPDATE_FILE_LOCATION = None

    #==========================================================================#
    #==========================================================================#
    # Not implemented functions of the class                                   #
    #==========================================================================#
    #==========================================================================#
    @classmethod
    def GetRelevantPlatform(cls):
        """ The platform relevant for this Update. The value should be 
            identical to the result of Utils.GetSystemPlatform() under the 
            relevant platform, otherwise, the Updater won't be chosen by 
            the Update module.
        """
        raise NotImplementedError('IUpdater.GetRelevantPlatform')

    @classmethod
    def DownloadUpdate(cls, url_to_download, latest_version):
        """ Download the zip file of the latest version, and places it in the 
            relevant location. The file name format of the downloaded file is:
            SubiT_<version>.zip, i.e. for version 2.0.1: SubiT_2-0-1.zip

            The function returns True if the download succeeded, else False.
        """
        raise NotImplementedError('IUpdater.DownloadUpdate')

    @classmethod
    def UpdateFileIsWaitingInDirectory(cls):
        """ Check if there is a new update files under UPDATE_FILE_LOCATION.
            The check is performed against the file name - if the version in
            the file name is higher than our current version, it's relevant.
            The function is called on each start-up of the program if the
            ShouldAutoUpdate() function returns True. The function is looking
            for the first newer version in the directory.

            The function returns a tuple of:
                bool update_is_wating  - True if there is a new update files
                str  full_path_to_file - Full path to the relevant update file 
                                         if there's any
        """
        raise NotImplementedError('IUpdater.UpdateFilesIsWaitingInDirectory')

    @classmethod
    def ApplyUpdate(cls, update_file_path):
        """ Extract the content from the zip file and replace the relevant 
            files on the in the current version. The function will start only 
            if the update file is from a newer version than the current one. 
        """
        raise NotImplementedError('IUpdater.ApplyUpdate')

    #==========================================================================#
    #==========================================================================#
    # Implemented functions of the class                                       #
    #==========================================================================#
    #==========================================================================#
    @classmethod
    def CurrentVersion(cls):
        """ Current version of SubiT as str. i.e. 2.0.0 """
        from Settings.Config import SubiTConfig
        return SubiTConfig.Singleton().getStr('Global', 'version')

    @classmethod
    def ShouldAutoUpdate(cls):
        """ Return the boolean from Updates.auto_update in the config. 

            Notice: If the implementation of the IUpdater is not intended to 
            applying updates, the function should always return False 
        """
        from Settings.Config import SubiTConfig
        return SubiTConfig.Singleton().getBoolean\
            ('Updates', 'auto_update', False)

    @classmethod
    def ShouldCheckUpdates(cls):
        """ Return the boolean from Updates.check_updates in the config """
        from Settings.Config import SubiTConfig
        return SubiTConfig.Singleton().getBoolean\
            ('Updates', 'check_updates', True)

    @classmethod
    def LastUpdateTime(cls):
        """ Return an integer from Updates.last_update_check in the config """
        from Settings.Config import SubiTConfig
        return SubiTConfig.Singleton().getInt('Updates', 'last_update_check', 0)

    @classmethod
    def IsUpdateFileName(cls, file_name):
        """ Check if the file name is in format of SubiT_<version>.zip """
        return file_name.startswith('SubiT_') and file_name.endswith('.zip')

    @classmethod
    def FromUpdateFileNameToVersion(cls, update_file_name):
        """ Convert a legitimate update file name to version. for example:
            from "SubiT_2-0-0.zip" to "2.0.0".
        """
        if cls.IsUpdateFileName(update_file_name):
            version = update_file_name.replace('SubiT_', '').replace('.zip', '')
            return version.replace('-', '.')
        return None

    @classmethod
    def FromVersionToUpdateFileName(cls, version):
        """ Convert a version to a legitimate update file name. for example:
            from "2.0.0" to "SubiT_2-0-0.zip".
        """
        return 'SubiT_' + version.replace('.', '-') + '.zip'

    @classmethod
    def IsNewerVersion(cls, our_version, other_version):
        """ Checks our version against other version. 

            The function return True only if the other_version is newer, in any
            other case, i.e. if the version are equal, or we got a newer version
            the return value is False. In any case of failure, we return False.
        """
        _is_newer = False

        _major_greater = False
        _major_older   = False
        _minor_greater = False
        _minor_older   = False
        _build_greater = False
        _build_older   = False

        try:
            _arr_our_version   = [int(i) for i in our_version.split('.')]
            _arr_other_version = [int(i) for i in other_version.split('.')]
            # If the str are equals than we got the latest
            if our_version == other_version:
                _is_newer = False
            else:
                if _arr_other_version[0] > _arr_our_version[0]: 
                    _major_greater = True
                elif _arr_other_version[0] < _arr_our_version[0]:
                    _major_older = True
                
                if _arr_other_version[1] > _arr_our_version[1]:
                    _minor_greater = True
                if _arr_other_version[1] < _arr_our_version[1]:
                    _minor_older = True

                if _arr_other_version[2] > _arr_our_version[2]:
                    _build_greater = True
                if _arr_other_version[2] < _arr_our_version[2]:
                    _build_older = True

        except Exception as eX:
            pass
        
        if _major_greater:
            _is_newer = True
        elif not _major_older and _minor_greater:
            _is_newer = True
        elif not _major_older and not _minor_older and _build_greater:
            _is_newer = True
        else:
            _is_newer = False

        return _is_newer


    @classmethod
    def IsLatestVersion(cls, force_check = False):
        """ Check wether we have the latest version of SubiT for the current
            platform or not. The check is made against LATEST_VERSION_PAGE.
            
            The function returns a tuple of:
                is_latest  - True if we got the latest else False
                latest_ver - The latest version number
                latest_url - Url to the relevant zip file download
        """
        import json

        from Utils import PerformRequest, WriteDebug, CurrentTime
        from Settings.Config import SubiTConfig
               
        _is_latest  = True
        _latest_url = None
        _latest_ver = None
        _last_check = SubiTConfig.Singleton().getInt\
            ('Updates', 'last_update_check', 0)
        WriteDebug('Checking if we got the latest versions')
        if (CurrentTime() - _last_check < cls.TIME_BETWEEN_CHECKS and 
            not force_check):
            WriteDebug('No need to check for updates right now')
            _is_latest = True
        else:
            WriteDebug('Time to check for updates')
            try:
                # The json format is:
                # {"version": "<version_number>", 
                #  "location": "<zip_file_location>"}
                _latest_ver_info = json.loads\
                    (PerformRequest(cls.SUBIT_DOMAIN, cls.LATEST_VERSION_PAGE))
            except Exception as eX:
                WriteDebug('Json failure: %s' % eX)
                return (_is_latest, _latest_ver, _latest_url)

            WriteDebug('Latest version %s' % _latest_ver_info)
            SubiTConfig.Singleton().setValue\
                ('Updates', 'last_update_check', CurrentTime())
            _current_ver = cls.CurrentVersion()
            _latest_ver  = _latest_ver_info['version']
            _latest_url  = _latest_ver_info['location']

            _is_latest = not cls.IsNewerVersion(_current_ver, _latest_ver)
            if _is_latest:
                WriteDebug('Got latest version')
            # Else, check for any kinds of version different
            else:
                WriteDebug('We have an old version')
        
        return (_is_latest, _latest_ver, _latest_url)