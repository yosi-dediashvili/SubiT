from cx_Freeze import setup, Executable

import SubiT, Utils

import shutil
import os
import sys
import time

src_dir_path    = r'D:\Programming\SubiT\src'
handlers_path   = r'D:\Programming\SubiT\src\SubHandlers'
build_path      = r'D:\Programming\SubiT\src\build'
dropbox_path    = r'D:\Dropbox\SubiT\src'
org_path        = os.path.join(build_path, 'exe.win32-2.7')
dest_path       = os.path.join(build_path, 'SubiT_%s' % SubiT.VERSION)
helpers_path    = os.path.join(build_path, 'helpers')
win32_path		= dest_path + '_Win32'
linux_path      = dest_path + '_Linux'
upgrade_path    = dest_path + '_Upgrade'

SubiT.DEBUG = False #Change Debug mode to false for less logs
Utils.DEBUG = False

#os.chdir(build_path.replace(r'\build', ''))

#remove dest_path, in order to start a clean session
if (os.path.exists(win32_path)):
    shutil.rmtree(win32_path)


#fake build param
sys.argv = [sys.argv[0], 'build_exe']

print 'Sleeping for 3 secs...'
time.sleep(3)

#Copy additional files							  
shutil.copytree(helpers_path, win32_path)
shutil.copytree(handlers_path, os.path.join(win32_path, 'SubHandlers'), ignore=shutil.ignore_patterns('*.py', '.svn'))

buildOptions = dict(build_exe=win32_path, optimize=2, include_files=['Images'],# excludes=['SubHandlers'],
                    copy_dependent_files=True, create_shared_zip=True, compressed=True, bin_path_excludes=['.svn'] )


setup(name="SubiT", 
      version=SubiT.VERSION, 
      description="SubiT - Download subtitles with just one click", 
      options=dict(build_exe = buildOptions),
      executables=[Executable("SubiT.py", 
                              base='Win32GUI' if not SubiT.DEBUG else 'Console',
							  icon='Images\\icon.ico',
                              compress=True,
                              targetDir=win32_path,
                              copyDependentFiles=True)])




try:
    if (os.path.exists(linux_path)):
        shutil.rmtree(linux_path)
except: pass

shutil.copytree(src_dir_path, linux_path, ignore=shutil.ignore_patterns('*_Linux*', 'Olds', 'build', '.svn', '*.py', '__pycache__', 'setup.py*', '*.bat', '*.ini'))
shutil.copy(os.path.join(helpers_path, 'README.txt'), linux_path)
shutil.copy(os.path.join(helpers_path, 'Settings\\config.ini'), os.path.join(linux_path, 'Settings'))

"""
try:
    if (os.path.exists(upgrade_path)):
        shutil.rmtree(upgrade_path)
except: pass    
shutil.copytree(dest_path, upgrade_path, ignore=shutil.ignore_patterns('*.pyd', 'imageformats', 'Images', '*.dll', '*.bat', '*.exe'))
"""

try:
    if (os.path.exists(dropbox_path)):
        shutil.rmtree(dropbox_path)
    shutil.copytree(src_dir_path, dropbox_path, ignore=shutil.ignore_patterns('*_Linux*', 'Olds', 'build', '.svn', '*.pyc', '__pycache__'))
except: pass


