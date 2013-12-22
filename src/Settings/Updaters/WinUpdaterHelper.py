""" An external application for performing the update after is was downloaded
    from the net. This file is compiled into an exe file for windows platform
    and launch when the ApplyUpdate method of WinUpdater is called.

    The module will extract the zip file if it exists, and execute the update
    manifest for the windows (update_manifest_for_win.py) platform if it exists
    inside the zip.

    The executable should get the path to the update file as the first arg,
    otherwise, immidiate exit will be performed. Any other parameters that was
    passed to SubiT in the first place, should be passed after update file 
    parameter.
"""


import sys
import zipfile
import os
import shutil

from Settings.Config import CONFIG_FILE_NAME, SubiTConfig
from Utils import GetProgramDir

_subit_dir = None
def SubitDir():
    global _subit_dir
    if not _subit_dir:
        # Because we're running from the standalone of the updater, the 
        # function will return The inner directory, and not SubiT's root one
        _subit_dir = GetProgramDir().replace('Settings\\Updaters', '')
    return _subit_dir

def PrintOut(message):
    print message

MANIFEST_NAME = 'update_manifest_for_win.py'
SUBIT_PATH    = os.path.join(SubitDir(), 'SubiT.exe')

def start_subit():
    PrintOut('Starting SubiT')
    args = sys.argv
    # Replace the updater path with subit's path
    args[0] = SUBIT_PATH
    # remove the update_file_path from the parameters
    args.pop(1)
    os.execv(SUBIT_PATH, args)

def main(update_file_path):
    if not os.path.exists(update_file_path):
        PrintOut('Update file is missing: %s' % update_file_path)
        return

    with zipfile.ZipFile(update_file_path) as zfile:
        # Path of the config file inside the zip file
        _config_path_in_zip = '%s/%s' % \
            ('Settings', CONFIG_FILE_NAME)

        if MANIFEST_NAME in zfile.namelist():
            PrintOut('There is a manifest in the zip file')
            manifest_content = zfile.open(MANIFEST_NAME).read()
            exec(manifest_content)
        else:
            PrintOut('No manifest file in update zip')

        for _file_info in zfile.infolist():
            # If the file is the config file, we place it under a different
            # name in the Settings directory, and call the upgrade() method
            # of SubiTConfig, and remove it afterwards.
            if _file_info.filename == _config_path_in_zip:
                _new_config_file_name = _config_path_in_zip.replace\
                    (CONFIG_FILE_NAME, 'new_config.ini')
                _new_config_full_path = os.path.join\
                    (SubitDir(), _new_config_file_name)
                _file_info.filename = _new_config_file_name
                PrintOut('Extracting new config file: %s' % _new_config_file_name)
                zfile.extract(_file_info, SubitDir())
                PrintOut('New config file extracted: %s' % _new_config_file_name)
                # Call the __init__ of SubiTConfig in order to set our path to 
                # the config file correctly
                SubiTConfig(os.path.join\
                    (SubitDir(), 'Settings', CONFIG_FILE_NAME))
                SubiTConfig.Singleton().upgrade(_new_config_full_path)
                os.remove(_new_config_full_path)
            # For each folder in the zip that is placed under the root and 
            # is not the Settings directory, we Check if it's already 
            # exists in the program's dir, and if so, remove it before 
            # extracting the new file. We do so in order to prevent 
            # conflicts between files and duplication (in providers for 
            # example, i.e. same provider but with different file name)
            elif (_file_info.file_size == 0 and 
                    # str.index gives the first index of '/'. We use that 
                    # fact to check if the first index is at the end of the 
                    # filename and therefor, the directory is under the root 
                    # and not inside another directory.
                    _file_info.filename.index('/') == \
                        len(_file_info.filename) - 1 and 
                    _file_info.filename != 'Settings/'):
                _dir_name = os.path.join\
                    (SubitDir(), _file_info.filename.replace('/', ''))
                if os.path.exists(_dir_name):
                    PrintOut('Deleting: %s' % _dir_name)
                    try:
                        shutil.rmtree(_dir_name)
                    except Exception as eX:
                        PrintOut('Failed on deletion: %s->%s' % (_dir_name, eX))
            # Extract all the files except for the manifest which we already
            # took care of.
            elif _file_info.filename != MANIFEST_NAME:
                PrintOut('Extracting: %s' % _file_info.filename)
                zfile.extract(_file_info, SubitDir())
                PrintOut('Extracted: %s' % _file_info.filename)
    PrintOut('Removing update file')
    os.remove(update_file_path)
    start_subit()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        PrintOut('Update file path should be passed as 2nd arg!')
        PrintOut('Usage: %s <update file> [original args]' % os.path.basename(sys.executable))