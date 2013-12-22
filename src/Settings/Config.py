import ConfigParser
import os

import Settings
import Utils

CONFIG_FILE_NAME = 'Config.ini'
CONFIG_FILE_PATH = os.path.join(Settings.SETTINGS_DIR_LOCATION, CONFIG_FILE_NAME)

def createDefaultFile():
    configs = """[Global]
; Section for global values
version = 1.3.0
is_first_run = True
close_on_finish = True
auto_update = False
check_updates = True
last_update_check = 0

[Handlers]
; Section for handlers related values
try_all_handlers = False
selected_handler = Hebrew - www.subscenter.org

[Registry]
; Section for registry (only for windows) values
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
    #Return the config value as str        
    def getStr(self, section, option, on_error_value = ''):
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as str' % (section, option))        
        try:    
            return_value = self._parser.get(section, option)
        except: 
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    #Return the config value as boolean
    def getBoolean(self, section, option, on_error_value = False):
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as boolean' % (section, option))        
        try:    
            return_value = self._parser.getboolean(section, option)
        except Exception as Ex: 
            raise Ex
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    #Return the config value as int
    def getInt(self, section, option, on_error_value = 0):
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as int' % (section, option))        
        try:    
            return_value = self._parser.getint(section, option)
        except: 
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

    #Return the config value as float
    def getFloat(self, section, option, on_error_value = 0.0):
        return_value = on_error_value

        Utils.WriteDebug('Retrieving: %s.%s as float' % (section, option))        
        try:    
            return_value = self._parser.getfloat(section, option)
        except: 
            Utils.WriteDebug('Failure while trying to get value, using default')
        Utils.WriteDebug('Value: %s.%s => %s' % (section, option, return_value))
        return return_value

#======================================================================================
#======================================================================================

    def setValue(self, section, option, value):
        Utils.WriteDebug('Setting value for: %s.%s => %s' % (section, option, value))
        self._parser.set(section, option, value)
        self.save()

    def save(self):
        with open(CONFIG_FILE_PATH, 'wb') as configFile:
            self._parser.write(configFile)

        #for some reason, when trying to access the settings value after setting them, exception is thrown.
        #we set the _Singelton to None in order to reload the config in the next call to the Singelton() function
        SubiTConfig._Singleton = None

    @staticmethod
    def Singleton():
        if SubiTConfig._Singleton == None:
            SubiTConfig()
        return SubiTConfig._Singleton