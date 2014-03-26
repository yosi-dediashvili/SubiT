import os

from EasyConfig.EasyConfig import EasyConfig

from Utils import WriteDebug
from Utils import GetProgramDir


CONFIG_FILE_NAME = 'config.ini'
CONFIG_FILE_PATH = os.path.join(GetProgramDir(), 'Settings', CONFIG_FILE_NAME)
    
def CreateDefaultConfigFile(config_path):
    configs = """
[Global]
version = 3.0.0
close_on_finish = False
default_directory = $DEFAULTDIR$
always_use_default_directory = False
subtitles_saving_extension = .srt
subtitles_extensions = ['.srt', '.sub', '.idx']


[Updates]
check_updates = True
auto_update = False
last_update_check = 0

[Providers]
languages_order = ['Hebrew']
providers_order = ['www.torec.net', 'www.subscenter.org', 'www.subtitle.co.il', 'www.opensubtitles.org', 'www.addic7ed.com']

[Flow]
in_depth_search = True
do_properties_based_rank = True

[Association]
associate_extensions = False
interaction_type = 0
extensions_keys = ['.mkv', '.avi', '.wmv', '.mp4', 'Directory']


[Gui]
show_log = True
remember_last_window_size = True
last_window_size = [600, 315]
remember_last_window_position = False
last_window_position = [0, 0]
"""

    settings_dir = os.path.join(GetProgramDir(), 'Settings')
    if not os.path.exists(settings_dir):
        os.mkdir(settings_dir)

    with open(config_path, 'w') as config_file:
        config_file.write(configs)


class SubiTConfig(EasyConfig):
    _singleton = None

    """ 
        SubiT extension for the EasyConfig module. For backwards compatibility, 
        the class implements the functions of the old SubiTConfig.
    """
    def __init__(self, config_path = None):
        """
            Our constructor will make sure that we create the config at the
            required path, if it's not there.
        """

        WriteDebug('Init SubiTConfig config file...')
        
        if config_path:
            WriteDebug('config_path was passed, using it for our config file')
            config_path = config_path
        else: 
            WriteDebug('config_path was not passed, using CONFIG_FILE_PATH instead')
            config_path = CONFIG_FILE_PATH

        if not os.path.exists(config_path) or not os.stat(config_path).st_size:
            WriteDebug('Config file is missing, creating one with the default values in: %s' % config_path)
            CreateDefaultConfigFile(config_path)

        WriteDebug('Config path: %s' % config_path)

        # Init the easy config.
        EasyConfig.__init__(self, config_path)
        SubiTConfig._singleton = self

# ============================================================================ #
# Functions to retrieve values from the config file                            #
# ============================================================================ #

    def _get(self, section, option):
        """ Retrieve the option from EasyConfig. """
        section = getattr(self, section)
        value = getattr(section, option)
        return value

    def getStr(self, section, option, on_error_value = ''):
        """ Return the config value as str. """
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as str' % (section, option))        
        try:    
            return_value = self._get(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    
    def getBoolean(self, section, option, on_error_value = False):
        """ Returns the config value as boolean. """
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as boolean' % (section, option))        
        try:    
            return_value = self._get(section, option)
        except Exception as Ex: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def getInt(self, section, option, on_error_value = 0):
        """. Return the config value as int. """
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as int' % (section, option))        
        try:    
            return_value = self._get(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def getFloat(self, section, option, on_error_value = 0.0):
        """ Return the config value as float. """
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as float' % (section, option))        
        try:    
            return_value = self._get(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value
    
    def getList(self, section, option, on_error_value = []):
        """ Return the config value as list. """
        return_value = on_error_value

        WriteDebug('Retrieving: %s.%s as list' % (section, option))        
        try:    
            return_value = self._get(section, option)
        except: 
            WriteDebug('Failure while trying to get value, using default')
        WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value


# ============================================================================ #
# Functions to store values in the config file                                 #
# ============================================================================ #
    def _set(self, section, option, value):
        section = getattr(self, section)
        setattr(section, option, value)

    def setValue(self, section, option, value):
        """ Set the value under the given section.option.value path. """
        WriteDebug('Setting value for: %s.%s => %s' % (section, option, value))
        self._set(section, option, value)
        self.save()

    def setList(self, section, option, list_values):
        """ Set the value under the given section.option.value path. """
        WriteDebug('Setting list value for: %s.%s => %s' % (section, option, list_values))
        self.setValue(section, option, list_values)

    def upgrade(self, new_config_path):
        """ 
            Perform an upgrade to the current configuration. The upgrade will
            keep the values of the current config file, and will only add the 
            new settings that are introduced in the new_config_path. The only
            exception to that rule is the version value, which gets updated.
        """
        WriteDebug('Starting upgrade procedure for configuration, using the file: %s' % new_config_path)
        if not os.path.exists(new_config_path):
            WriteDebug('The new_config_path is missing')
        else:
            WriteDebug('Init new parser for the config')
            upgrade_easy_config = EasyConfig(new_config_path)
            WriteDebug('Config file object created')

            EasyConfig.upgrade(self, upgrade_easy_config)
            # Update the version.
            self.Global.version = upgrade_easy_config.Global.version
                    
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
