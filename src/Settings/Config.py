import ConfigParser
import os

import Settings
import Utils

CONFIG_FILE_NAME = 'Config.ini'
CONFIG_FILE_PATH = os.path.join(Settings.SETTINGS_DIR_LOCATION, CONFIG_FILE_NAME)

def createDefaultFile():
    configs = """[Global]
version = 1.3.1
is_first_run = True
close_on_finish = False
auto_update = False
check_updates = True
last_update_check = 0

[Handlers]
selected_handler = Hebrew - www.Torec.net
advanced_features = True
primary_lang = Hebrew
secondary_lang = English

[Registry]
register_extensions = True
keys = .mkv|.avi|.wmv|.mp4|Directory"""
    if not os.path.exists(Settings.SETTINGS_DIR_LOCATION):
        os.mkdir(Settings.SETTINGS_DIR_LOCATION)
    with open(CONFIG_FILE_PATH, 'wb') as configFile:
        configFile.write(configs)


class SubiTConfig():
    #Stores the parser
    _parser    = None
    _Singleton = None
    def __init__(self):
        Utils.WriteDebug('Init Config File')
        self._parser = ConfigParser.ConfigParser()
        #If the file is missing, create it
        if not os.path.exists(CONFIG_FILE_PATH):
            Utils.WriteDebug('Config file is missing, creating default')
            createDefaultFile()
        Utils.WriteDebug('Config path: %s' % CONFIG_FILE_PATH)
        self._parser.read(CONFIG_FILE_PATH)
        SubiTConfig._Singleton = self
        Utils.WriteDebug('Config Singleton Created')
    
#======================================================================================#
# Functions to retrieve values from the config file                                    #
#======================================================================================# 
    def getStr(self, section, option, on_error_value = ''):
        """Return the config value as str """
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as str' % (section, option))        
        try:    
            return_value = self._parser.get(section, option)
        except: 
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    
    def getBoolean(self, section, option, on_error_value = False):
        """Return the config value as boolean"""
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as boolean' % (section, option))        
        try:    
            return_value = self._parser.getboolean(section, option)
        except Exception as Ex: 
            raise Ex
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def getInt(self, section, option, on_error_value = 0):
        """Return the config value as int"""
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as int' % (section, option))        
        try:    
            return_value = self._parser.getint(section, option)
        except: 
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def getFloat(self, section, option, on_error_value = 0.0):
        """Return the config value as float"""
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as float' % (section, option))        
        try:    
            return_value = self._parser.getfloat(section, option)
        except: 
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    def hasOption(self, section, option):
        """Return True if current config has the given option, otherwise, False"""
        has_opt = self._parser.has_option(section, option)
        Utils.WriteDebug('Is %s.%s exists? %s' % (section, option, has_opt))
        return has_opt

#======================================================================================
#======================================================================================

    def setValue(self, section, option, value):
        Utils.WriteDebug('Setting value for: %s.%s => %s' % (section, option, value))
        # If the section is missing, and we try to set the value, an exception will 
        # be raised, therfore, we create the section
        if not self._parser.has_section(section):
            Utils.WriteDebug('Missing section: %s, creating it' % section)
            self._parser.add_section(section)

        self._parser.set(section, option, value)
        self.save()

    def save(self):
        with open(CONFIG_FILE_PATH, 'wb') as configFile:
            self._parser.write(configFile)

        #for some reason, when trying to access the settings value after setting them, exception is thrown.
        #we set the _Singelton to None in order to reload the config in the next call to the Singelton() function
        SubiTConfig._Singleton = None

    def upgrade(self, new_config_path):
        """Function to perform upgrade of the current configuration, keeping the current values"""
        Utils.WriteDebug('Starting upgrade procedure for configuration, using the file: %s' % new_config_path)
        if not os.path.exists(new_config_path):
            Utils.WriteDebug('Upgrade config file is missing.')
        else:
            upgrade_parser = ConfigParser.ConfigParser()
            upgrade_parser.read(new_config_path)
            Utils.WriteDebug('Config file object created')
            #Iterate on all sections and values
            for upgrade_section in upgrade_parser.sections():
                for upgrade_item in upgrade_parser.items(upgrade_section):
                    #Upgrade only if the option is missing from current version
                    if not self.hasOption(upgrade_section, upgrade_item[0]) or (upgrade_section == 'Global' and upgrade_item[0] == 'version'):
                        Utils.WriteDebug('Adding new option to the configuration: %s.%s' % (upgrade_section, upgrade_item[0]))
                        self.setValue(upgrade_section, *upgrade_item)
        Utils.WriteDebug('Configuration upgrade procedure finished')

    @staticmethod
    def Singleton():
        if SubiTConfig._Singleton == None:
            SubiTConfig()
        return SubiTConfig._Singleton