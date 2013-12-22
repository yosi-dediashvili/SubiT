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
linux_path      = dest_path + '_Linux'

SubiT.DEBUG = False #Change Debug mode to false for less logs
Utils.DEBUG = False

#os.chdir(build_path.replace(r'\build', ''))

#remove dest_path, in order to start a clean session
if (os.path.exists(dest_path)):
    shutil.rmtree(dest_path)


#fake build param
sys.argv = [sys.argv[0], 'build_exe']

print 'Sleeping for 3 secs...'
time.sleep(3)

shutil.copytree(helpers_path, dest_path)    
shutil.copytree(handlers_path, os.path.join(dest_path, 'SubHandlers'), ignore=shutil.ignore_patterns('*.py', '.svn'))

buildOptions = dict(build_exe=dest_path, optimize=2, include_files=['Images', 'Settings\\config.ini'],# excludes=['SubHandlers'],
                    copy_dependent_files=True, create_shared_zip=True, compressed=True, bin_path_excludes=['.svn'] )


setup(name="SubiT", 
      version=SubiT.VERSION, 
      description="SubiT - Download subtitles with just one click", 
      options=dict(build_exe = buildOptions),
      executables=[Executable("SubiT.py", 
                              base='Win32GUI' if not SubiT.DEBUG else 'Console',
							  icon='Images\\icon.ico',
                              compress=True,
                              targetDir=dest_path,
                              copyDependentFiles=True)])


if (os.path.exists(linux_path)):
    shutil.rmtree(linux_path)
shutil.copytree(src_dir_path, linux_path, ignore=shutil.ignore_patterns('*_Linux*', 'Olds', 'build', '.svn', '*.py', '__pycache__', 'setup.py*', '*.bat'))
shutil.copy(os.path.join(helpers_path, 'README.txt'), linux_path)

if (os.path.exists(dropbox_path)):
    shutil.rmtree(dropbox_path)

shutil.copytree(src_dir_path, dropbox_path, ignore=shutil.ignore_patterns('*_Linux*', 'Olds', 'build', '.svn', '*.pyc', '__pycache__'))
