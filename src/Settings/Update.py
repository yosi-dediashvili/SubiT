import json
import time
import urllib
import os
import shutil
#import urllib.request
import zipfile

from Settings import Config
from Settings.UpdateGui import UpdateGui 
import Utils
import SubiT

TIME_BETWEEN_CHECKS     = 60 * 60 * 12 #Check every 12 hours

SUBIT_DOMAIN            = r'www.subit-app.sourceforge.net'
LATEST_VERSION_SITE     = r'http://subit-app.sourceforge.net/latest_version.html'
LATEST_VERSION_LINK     = r'http://sourceforge.net/projects/subit-app/files/latest/download'
SHOULD_AUTO_UPDATE      = Config.SubiTConfig.Singleton().getBoolean('Global', 'auto_update', False)
SHOULD_CHECK_UPDATES    = Config.SubiTConfig.Singleton().getBoolean('Global', 'check_updates', True)
LAST_UPDATE_TIME        = Config.SubiTConfig.Singleton().getInt('Global', 'last_update_check', 0)
CURRENT_VERSION         = SubiT.VERSION


def writeLog(message):
   UpdateGui.Singleton().writeLog(message)
   Utils.WriteDebug(message)

def checkForUpdate():
    """function to retrieve latest version info for the site
    latest_version.html page is a json'd page, with the following format:
    {"version": "<version_number>", "location": "<zip_file_location>"}"""

    Utils.WriteDebug('Getting update info: %s' % LATEST_VERSION_SITE)
    latest_version = json.loads(Utils.performrequest(SUBIT_DOMAIN, LATEST_VERSION_SITE, '', Utils.HttpRequestTypes.GET, ''))
    Utils.WriteDebug('Got update info')
    return latest_version

def handleUpdateZipFile(zip_location = os.path.join(Utils.PROGRAM_DIR_PATH, 'latest_version.zip')):
    """Function to handle the update zip file after SubiT restarts"""

    #If zip file exists
    if os.path.exists(zip_location):
        Config.SubiTConfig.Singleton().save() #Save and close the config file
        with zipfile.ZipFile(zip_location) as zfile:
            for fileInfo in zfile.filelist:
                #If the file is directory (we check for file size...), and the directory is first in the tree (we are not inside another directory)
                if fileInfo.file_size == 0 and fileInfo.filename.index('/') == len(fileInfo.filename) -1:
                    dir_name = os.path.join(Utils.PROGRAM_DIR_PATH, fileInfo.filename.split('/')[0]) #dir name in SubiT's dir
                    if os.path.exists(dir_name):
                        #If the direcotry exists in SubiT we remove it in order to avoid problems after the 
                        #update (conflicts between files, to Duplication in handlers and so on...)
                        Utils.WriteDebug('Deleting: %s' % dir_name)
                        try:
                            shutil.rmtree(dir_name)
                        except Exception as eX:
                            Utils.WriteDebug('Failed on deletion: %s->%s' % (dir_name, eX.message))
                Utils.WriteDebug('Extracting: %s' % fileInfo.filename)
                #after cleaning all, extract the item
                zfile.extract(fileInfo, Utils.PROGRAM_DIR_PATH)
                Utils.WriteDebug('Extracted: %s' % fileInfo.filename)
        Utils.WriteDebug('Removing update file')
        os.remove(zip_location)
        Utils.WriteDebug('Restarting SubiT')
        Utils.restart()



def isLatestVersion(force = False):
    """function to decide wether our version is the latest version or not"""
    
    #Default values
    is_latest   = False
    latest_url  = ''
    latest_ver  = ''

    #If last check wasn't later than 12 hours back, we use the last result
    if int(time.time()) - LAST_UPDATE_TIME < TIME_BETWEEN_CHECKS and not force:
        writeLog('No need to check for updates right now -> returning True')
        #Notice that we're not setting the last_update_check value in the config. 
        #If we do set it, we'll never get pass the first update check (we'll always return true...)
        is_latest = True
    else:
        writeLog('Time to check for updates')
        latest_version_info = checkForUpdate()
        #Set last_update_check to current time
        Config.SubiTConfig.Singleton().setValue('Global', 'last_update_check', str(int(time.time())))

        latest_ver  = latest_version_info['version']    #latest version number
        latest_url  = latest_version_info['location']   #latest version zip file location

        #devide both current version and latest version into [major, minor, build] list
        div_current_version = [int(i) for i in CURRENT_VERSION.split('.')]
        div_latest_version  = [int(i) for i in latest_ver.split('.')]

        #If array's are equal, it's the same version
        if CURRENT_VERSION == latest_ver:
            is_latest = True
        #Else, check for all kinds of version different
        elif div_latest_version[0] >= div_current_version[0]: 
            if div_latest_version[1] >= div_current_version[1]:
                if (div_latest_version[2] > div_current_version[2] or #build version
                    div_latest_version[1] > div_current_version[1] or #minor version 
                    div_latest_version[0] > div_current_version[0]):  #major version
                    is_latest = False

    if is_latest: 
        writeLog('Got latest version: %s' % CURRENT_VERSION) 
    else: 
        writeLog('Update is needed, latest version is: %s' % latest_ver)
        
    return (is_latest, latest_url, latest_ver)


def performUpdate(force = False, do_auto = True):
    """this function will check for the update, and if needed (and requested), 
    will perform the update operation (download&install)"""

    #If we should'nt update, quit procedure
    if not SHOULD_CHECK_UPDATES:
        Utils.WriteDebug('Update: Global.check_updates is False')
    #If we should
    else:
        (is_latest, latest_url, latest_version) = isLatestVersion(force)
        #If we don't have the latest update
        if not is_latest: 
            Utils.GuiInstance.showUpdate()
            writeLog('Global.auto_update is %s' % str(SHOULD_AUTO_UPDATE))
            #If we should perform auto_update
            if SHOULD_AUTO_UPDATE and do_auto:
                zip_location = os.path.join(Utils.PROGRAM_DIR_PATH, 'latest_version.zip')
                writeLog('Downloading Update')
                #Download the zip file
                urllib.urlretrieve(latest_url, zip_location)
                writeLog('Update file retrieved')
                #After download is finished, restart SubiT, so we'll enter the handleUpdateZipFile function from clean state  
                writeLog('SubiT will now restart')
                time.sleep(2)
                Utils.restart()
            else:
                update_message = 'New version of SubiT is available!\r\nYour version is: %s, latest version is: %s.\r\n\r\nClick Yes for redirection to the download page.' % (CURRENT_VERSION, latest_version)
                UpdateGui.Singleton().askUserForLink(update_message, LATEST_VERSION_LINK)

    UpdateGui.Singleton().doCloseEvent()