from cx_Freeze import setup, Executable
import SubiT
import shutil
import os
import sys

build_path      = r'D:\Programming\SubiT\src\build'
org_path        = os.path.join(build_path, 'exe.win32-2.7')
dest_path       = os.path.join(build_path, 'SubiT_%s' % SubiT.VERSION)
helpers_path    = os.path.join(build_path, 'helpers')

os.chdir(build_path.replace(r'\build', ''))

#remove dest_path, in order to start a clean session
if (os.path.exists(dest_path)):
    shutil.rmtree(dest_path)


#fake build param
#sys.argv = [sys.argv[0], 'build']
sys.argv = [sys.argv[0], 'bdist_msi']

buildOptions = dict(optimize=2)#, include_files=[('build\\helpers','')])
setupOptions = dict(skip_build=0, bdist_dir=dest_path)
setup(name="SubiT", 
      version=SubiT.VERSION, 
      description="SubiT - Download subtitles with just one click", 
      options=dict(build_exe = buildOptions, bdist_msi=setupOptions),
      executables=[Executable("SubiT.py", 
                              base='Win32GUI',
							  icon='icon.ico')])

							  
#os.rename(org_path, dest_path)
'''
shutil.rmtree(os.path.join(dest_path, 'tcl'))
shutil.rmtree(os.path.join(dest_path, 'tk'))

for (current_dir, dirs, files) in os.walk(helpers_path):
    for f in files:
        cd = current_dir
        if (helpers_path in current_dir):
            cd = current_dir.replace(helpers_path , '').lstrip('\\')
        
        destination = os.path.join(dest_path, cd)
        if not os.path.exists(destination):
            print 'creating dir: %s' %  destination
            os.mkdir(destination)
        print 'copying {0}\\{2} -> {1}\\{2}'.format(current_dir, destination, f)
        shutil.copy(os.path.join(current_dir,f), destination)

print 'Done!'
'''