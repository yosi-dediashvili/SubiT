import os

from Utils import WriteDebug
from Utils import GetProgramDir

import ConfigParser as configparser


CONFIG_FILE_NAME = 'config.ini'
CONFIG_FILE_PATH = os.path.join(GetProgramDir(), 'Settings', CONFIG_FILE_NAME)
    
def CreateDefaultConfigFile(config_path):
    configs = """
[Global]
version = 2.2.3
close_on_finish = False
default_directory = $DEFAULTDIR$
always_use_default_directory = False
subtitles_saving_extension = .srt
subtitles_extensions = .srt|.sub|.idx

[Updates]
check_updates = True
auto_update = False
last_update_check = 0

[Providers]
languages_order =
providers_order = www.torec.net|www.subscenter.org|www.subtitle.co.il|www.opensubtitles.org|www.subscene.com|www.addic7ed.com

[Flow]
in_depth_search = True
do_properties_based_rank = True

[Association]
associate_extensions = False
interaction_type = 0
extensions_keys = .mkv|.avi|.wmv|.mp4|Directory

[Gui]
show_log = False
remember_last_window_size = True
last_window_size = 600|280
remember_last_window_position = False
last_window_position = 0|0
"""

    settings_dir = os.path.join(GetProgramDir(), 'Settings')
    if not os.path.exists(settings_dir):
        os.mkdir(settings_dir)

    with open(config_path, 'w') as config_file:
        config_file.write(configs)


class SubiTConfig():
    LIST_DELIMITER = '|'

    _parser    = None
    _singleton = None
    # Cache Names
    MOVIE_EXT_CACHE_NAME = "MovieExt"
    SUBTITLE_EXT_CACHE_NAME = "SubtitleExt"

    def __init__(self, config_path = None):
        """ The constuctor of SubiTConfig will create a new config file if the
            current one is missing. If config_path is not given, we will use
            the global value of CONFIG_FILE_PATH for the file path
        """
        WriteDebug('Init SubiTConfig config file...')
        self._parser = configparser.ConfigParser()
        
        if config_path:
            WriteDebug('config_path was passed, using it for our config file')
            self.config_path = config_path
        else: 
            WriteDebug('config_path was not passed, using CONFIG_FILE_PATH instead')
            self.config_path = CONFIG_FILE_PATH

        if not os.path.exists(self.config_path) or \
            not os.stat(self.config_path).st_size:
            WriteDebug('Config file is missing, creating one with the default values in: %s' % self.config_path)
            CreateDefaultConfigFile(self.config_path)

        WriteDebug('Config path: %s' % self.config_path)
        self._parser.read(self.config_path)
        SubiTConfig._singleton = self
        WriteDebug('Config Singleton Created')
        #init new cache dictionary, this param will saved all the common values from the config file
        self._cache = {}


#==============================================================================#
# fast access to common values                                                 #
#==============================================================================#
    def getMoviesExtensions(self, with_dot = True):
        """Return all the extensions associated to movie files as it apear in
        the config file. Extensions are in lower case."""

        #check if something saved in cache
        if self._cache.get(self.MOVIE_EXT_CACHE_NAME) is not None:
            return self._cache.get(self.MOVIE_EXT_CACHE_NAME)

        _ext = self.getList('Association', 'extensions_keys',
                                           ['.mkv', '.avi', '.wmv', '.mp4'])
        _ext =  list(map(str.lower, _ext))
        if not with_dot:
            _ext = list(map(lambda e: e.lstrip('.'), _ext))

        #set cache value:
        self._cache[self.MOVIE_EXT_CACHE_NAME] = _ext
        return _ext

    def getSubtitlesExtensions(self, with_dot = True):
        """Return all the extensions associated to subtitle files as it apear in
        the config file. Extensions are in lower case."""

         #check if something saved in cache
        if self._cache.get(self.SUBTITLE_EXT_CACHE_NAME) is not None:
            return self._cache.get(self.SUBTITLE_EXT_CACHE_NAME)

        _ext = self.getList('Global', 'subtitles_extensions',
                                           ['.srt', '.sub', '.idx'])
        _ext = list(map(str.lower, _ext))
        if not with_dot:
            _ext = list(map(lambda e: e.lstrip('.'), _ext))

        #set cache value:
        self._cache[self.SUBTITLE_EXT_CACHE_NAME] = _ext
        return _ext
#==============================================================================#
# Functions to retrieve values from the config file                            #
#==============================================================================#
    def getStr(self, section, option, on_error_value = ''):
        """Return the config value as str """
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as str' % (section, option))        
        try:    
            return_value = self._parser.get(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    
    def getBoolean(self, section, option, on_error_value = False):
        """Return the config value as boolean"""
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as boolean' % (section, option))        
        try:    
            return_value = self._parser.getboolean(section, option)
        except Exception as Ex: 
            raise Ex
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def getInt(self, section, option, on_error_value = 0):
        """Return the config value as int"""
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as int' % (section, option))        
        try:    
            return_value = self._parser.getint(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def getFloat(self, section, option, on_error_value = 0.0):
        """Return the config value as float"""
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as float' % (section, option))        
        try:    
            return_value = self._parser.getfloat(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value
    
    def getList(self, section, option, on_error_value = []):
        """Return the config value as list"""
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as list' % (section, option))        
        try:    
            str_value = self.getStr(section, option, '')
            if str_value != '':
                return_value = str_value.split(SubiTConfig.LIST_DELIMITER)
            else:
                return_value = []
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def hasOption(self, section, option):
        """ Return True if current config has the given option, otherwise, 
            False """
        has_opt = self._parser.has_option(section, option)
        WriteDebug('Is %s.%s exists? %s' % (section, option, has_opt))
        return has_opt

#==============================================================================#
# Functions to store values in the config file                                 #
#==============================================================================#
    def setValue(self, section, option, value):
        """ Set the value under the given section.option.value path. values 
            are converted to str types """
        WriteDebug('Setting value for: %s.%s => %s' % (section, option, value))
        # If the section is missing, and we try to set the value, an 
        # exception will be raised, therfore, we create the section
        if not self._parser.has_section(section):
            WriteDebug('Missing section: %s, creating it' % section)
            self._parser.add_section(section)

        self._parser.set(section, option, str(value))
        self.save()

    def setList(self, section, option, list_values):
        """ Set the value under the given section.option.value path. The list 
            is converted to piplined str """
        WriteDebug('Setting list value for: %s.%s => %s' % (section, option, list_values))
        self.setValue\
            (section, option, SubiTConfig.LIST_DELIMITER.join(list_values))

    def save(self):
        """ Save the config to the config file. The path to the file is taken
            from self.config_path
        """
        with open(self.config_path, 'w') as config_file:
            self._parser.write(config_file)
        # For some reason, when trying to access the settings value after we 
        # set them, exception is thrown. we set the _singelton to None in order 
        # to reload the config in the next call to the Singelton() function
        SubiTConfig._singleton = None

    def upgrade(self, new_config_path):
        """ Perform an upgrade to the current configuration. The upgrade will
            keep the values of the current config file, and will only add the 
            new settings that are introduced in the new_config_path. The only
            exception to that rule is the version value, which gets updated.
        """
        WriteDebug('Starting upgrade procedure for configuration, using the file: %s' % new_config_path)
        if not os.path.exists(new_config_path):
            WriteDebug('The new_config_path is missing')
        else:
            WriteDebug('Init new parser for the config')
            upgrade_parser = configparser.ConfigParser()
            upgrade_parser.read(new_config_path)
            WriteDebug('Config file object created')
            # Iterate on all sections and values
            for upgrade_section in upgrade_parser.sections():
                # upgrade_item is a tuple of (name, value) for an option, so we
                # access the option name by refering to the 0 index
                for upgrade_item in upgrade_parser.items(upgrade_section):
                    # Upgrade only if the option is missing from current config
                    if not self.hasOption(upgrade_section, upgrade_item[0]):
                        WriteDebug('Adding new option to the configuration: %s.%s' % (upgrade_section, upgrade_item[0]))
                        self.setValue(upgrade_section, *upgrade_item)
                    # Or if this is the version value, and therfor, we need to
                    # upgrade to the new value
                    elif upgrade_section == 'Global' and upgrade_item[0] == 'version':
                        WriteDebug('Upgrading the Global.version value to: ' % upgrade_item[1])
                        self.setValue(upgrade_section, *upgrade_item)
        WriteDebug('Configuration upgrade procedure finished')

    @staticmethod
    def Singleton():
        """ Get the singleton object of the SubiTConfig. If the _singleton is 
            None, we will call the Init function of SubiTConfig in order to set
            the _singleton again
        """
        if SubiTConfig._singleton == None:
            SubiTConfig()
        return SubiTConfig._singleton


#==============================================================================#
#   Get the config singelton                                                     #
#==============================================================================#
def getConfig():
    return SubiTConfig.Singleton()


#==============================================================================#
#   Folder functions from Utils , using cache now !                              #
#==============================================================================#
def GetSubtitlesExtensions(with_dot = True):
    """Return all the extensions associated to subtitle files as it apear in
    the config file. Extensions are in lower case."""
    return getConfig().getSubtitlesExtensions()

def GetMoviesExtensions(with_dot = True):
    """Return all the extensions associated to movie files as it apear in
    the config file. Extensions are in lower case."""
    return getConfig().getMoviesExtensions()