import shutil
import os
import sys
import time
from subprocess import check_output
from subprocess import call
from distutils.sysconfig import get_python_lib
import astor
import ast
import inspect
import platform


def IsWindowsPlatform():
    """Return True if the system's OS is Windows, else False."""
    return platform.system() == 'Windows'

# For some reason, python wont try to load modules from that 
# directory under my linux
if not IsWindowsPlatform():
    sys.path.append(get_python_lib())


def getPlatformName():
    if IsWindowsPlatform(): 
        return "win32"
    else:
        raise NotImplementedError("Only win32 is present.")

# We get the path of SubiT dynamically. This file (setup.py) is located inside
# the build directory, so calling dirname() twice, will give us SubiT's root
# directory.
current_path    = os.path.abspath(__file__)
base_path       = os.path.dirname(os.path.dirname(current_path))
src_dir_path    = os.path.join(base_path, 'src')
build_dir_path  = os.path.join(base_path, 'build')


# Append the src folder the sys.path in 
# order to get access to the modules
sys.path.append(src_dir_path)
sys.path.append(build_dir_path)

# ============================================================================ #
# Subit distribution defenitions                                               #
# ============================================================================ #
subit_name          = 'SubiT'
subit_desc          = 'SubiT - Download subtitles with just one click'
subit_author        = 'subit-app'
subit_author_mail   = 'SubiT.app@mail.com'
subit_url           = r'http://www.subit-app.sf.net'
from Settings.Config import SubiTConfig
subit_version       = \
    SubiTConfig.Singleton().getStr('Global', 'version', '0.0.0')
# Unload the module right away to avoid problems
del SubiTConfig
sys.path.remove(src_dir_path)
# ============================================================================ #
# ============================================================================ #


build_platform_dir_path     = os.path.join(build_dir_path, getPlatformName())
build_platform_helpers_path = os.path.join(build_platform_dir_path, "_helpers")
build_version_dir_path      = os.path.join(build_platform_dir_path, subit_version)

build_bin_path      = os.path.join(build_version_dir_path, 'bin')
build_setup_path    = os.path.join(build_version_dir_path, 'setup')
build_dist_path     = os.path.join(build_version_dir_path, 'dist')
build_src_dir_path  = os.path.join(build_version_dir_path, '__src')
build_tmp_dir_path  = os.path.join(build_version_dir_path, '__tmp')

subit_proxy_py_path = os.path.join(build_src_dir_path, 'SubiTProxy.py')
providers_path      = os.path.join(build_src_dir_path, 'SubProviders')

pyinstaller_build_path = os.path.join\
    (get_python_lib(), r'PyInstaller\utils\Build.py')


# ============================================================================ #
# Platform independent functions                                               #
# ============================================================================ #
def log(message):
    message = '[Setup]-[%s] => %s' % (time.strftime('%I:%M:%S'), message)
    print(message)

def printSubitDefs():
    log('subit_name:          %s' % subit_name)
    log('subit_desc:          %s' % subit_desc)
    log('subit_author:        %s' % subit_author)
    log('subit_author_mail:   %s' % subit_author_mail)
    log('subit_version:       %s' % subit_version)

def removeTreeAndWaitForFinish(dir, wait_time = 0.10, wait_after = 3):
    log('Removing: %s' % dir)
    if os.path.exists(dir):
        shutil.rmtree(dir)

    while os.path.exists(dir):
        time.sleep(wait_time)
    log('Removed: %s' % dir)
    time.sleep(wait_after)

def createAndMoveToTempBuildDir():
    removeTreeAndWaitForFinish(build_tmp_dir_path)
    log("Moving to temp dir: %s" % build_tmp_dir_path)
    os.makedirs(build_tmp_dir_path)
    os.chdir(build_tmp_dir_path)

def copySrcDir(destination):
    try:
        removeTreeAndWaitForFinish(destination)
        
        log('Copying src dir to: %s' % destination)
        shutil.copytree(src_dir_path, destination, 
                        ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
        log('Finished copying src dir to: %s' % destination)
        return True
    except Exception as eX:
        log('Failed copying the src dir to: %s' % destination)
        log(eX)
        return False

def copySrcDirToBuildDir():
    """ Create replication of the src folder in the build directory in 
        order to run the minifier on it.
    """
    return copySrcDir(build_src_dir_path)

def getAstFromSourceFile(file_path):
    """ 
        Convert the given source inside the file_path to an AST instance. 
    """
    return astor.parsefile(file_path)

def getSourceFileFromAst(ast_tree, file_path):
    """
        Convert the AST back to python source, and saves it under file_path.
    """
    source = astor.to_source(ast_tree)
    open(file_path, "w").write(source)


class WriteDebugRemover(ast.NodeTransformer):
    def visit_Expr(self, node):
        # If it's a function call.
        if hasattr(node, "value") and isinstance(node.value, ast.Call):
            call = node.value
            # If it's a call to WriteDebug
            if isinstance(call.func, ast.Name) and call.func.id == "WriteDebug":
                log("Removing WriteDebug call from line: %s,%s" % 
                    (call.lineno, call.col_offset))
                node.value = ast.Pass()
                return node
        # In any other case, return the node.
        return node
def removeWriteDebugCalls(ast_tree):
    """ Replaces any call to WriteDebug in the ast tree with pass. """
    WriteDebugRemover().visit(ast_tree)
    

class WriteDebugFilePathAdder(ast.NodeTransformer):
    def __init__(self, py_file_path):
        """ 
            Init with the path to the file that should be added to the 
            WriteDebug calls.
        """
        self.py_file_path = py_file_path
    def visit_Expr(self, node):
        # If it's a function call.
        if hasattr(node, "value") and isinstance(node.value, ast.Call):
            call = node.value
            # If it's a call to WriteDebug
            if isinstance(call.func, ast.Name) and call.func.id == "WriteDebug":
                # If the argument count to the function is 1 (meaning that the
                # calling_file was not passed by the caller).
                if len(call.args) == 1:
                    call.args.append(ast.Str(self.py_file_path))
                    log("Adding calling_file to WriteDebug in line: %s,%s" %
                        (call.lineno, call.col_offset))
                    node.value = call
                    return node
        # In any other case, return the node.
        return node
def addFilePathToWriteDebug(ast_tree, file_path):
    """
        Adds the file_path as the second argument to the WriteDebug calls in 
        the ast tree.
    """
    WriteDebugFilePathAdder(file_path).visit(ast_tree)

def reformatPythonFile(py_file_path, debug):
    """ 
        Perform changes to the python file content. Currently, the calls to 
        WriteDebug are removed from the source.
    """
    log('Starting formation of py file: %s' % py_file_path)
    ast_tree = getAstFromSourceFile(py_file_path)
    if debug:
        addFilePathToWriteDebug(ast_tree, py_file_path)
    else:
        removeWriteDebugCalls(ast_tree)

    getSourceFileFromAst(ast_tree, py_file_path)
    log('Finished formation of py file: %s' % py_file_path)

def reformatPythonFiles(debug):
    """ 
        Reformats all the python files under build_src_dir_path. The reformat 
        is defined in the reformatPythonFile function. 
    """
    log('Starting formation of files')
    if os.path.exists(build_src_dir_path):
        def _isPyFile(f):
            return f.endswith('.py')
        for current_dir, dirs_in_dir, files_in_dir \
            in os.walk(build_src_dir_path):

            for f in files_in_dir:
                if _isPyFile(f):
                    py_file_path = os.path.join(current_dir, f)
                    reformatPythonFile(py_file_path, debug)
    else:
        log('Path is missing: %s' % build_src_dir_path)
    log('Finished formation of files!')
       
def minifyPyFilesInSrc():
    """ Produce a minified version of the src folder. The minified folder will
        be located in build_src_dir_path.
    """
    log('Starting minification of: %s' % build_src_dir_path)
    import minifier

    for dir_path, dir_names, file_names in os.walk(build_src_dir_path):
        # Locate the python files in the folder.
        py_files = list(filter(lambda f: f.endswith('.py'), file_names))
        for py_file in py_files:
            py_file_full_path = os.path.join(dir_path, py_file)

            # We're not touching the gui files. The minifier might remove 
            # text lines from there...
            if py_file_full_path.endswith('Gui.py'):
                log('Skipping GUI file: %s' % py_file_full_path)
                continue

            log('Minifying file: %s [%sKB]' % 
                    (py_file_full_path, 
                    round(os.stat(py_file_full_path).st_size / 1024, 2)))

            py_file_content = open(py_file_full_path, 'r').read()
            py_file_content_minified = minifier.minify(py_file_content)
            open(py_file_full_path, 'w').write(py_file_content_minified)
            log('File minified: %s [%sKB]' % 
                    (py_file_full_path, 
                    round(os.stat(py_file_full_path).st_size / 1024, 2)))
            log('-------------------------------------------------------')
    log('Finished minification of: %s' % build_src_dir_path)

def copySubProvidersFilesToDir(dest_dir):
    """ Will copy the files inside __src.SubProviders to dest_dir.SubProviders.
    """
    log('Copying SubProviders from [%s] to [%s]' % (providers_path, dest_dir))
    shutil.copytree(providers_path, dest_dir,
                    ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))

def executeInPythonInterpreter(command):
    """ Execute a command in the python interpreter, the function will add
        "python " before the command. the return value is the return value
        of check_output from subprocess.
    """
    log('Calling python with: %s' % command)
    command = 'python ' + command
    if IsWindowsPlatform():
        return check_output(command)
    else:
        return check_output(command, shell=True)

def getBuildStr(debug):
    if debug:
        return "debug"
    else:
        return "release"

def copyReadmeToDist():
    readme_path = os.path.join(base_path, "README.md")
    shutil.copy(readme_path, build_dist_path)
# ============================================================================ #
# ============================================================================ #



# ============================================================================ #
# Win32 building functions                                                     #
# ============================================================================ #

zip_name_format_win32       = "subit-%s-{build}-win32.zip" % subit_version
spec_file_base_win32        = os.path.join(build_platform_helpers_path, 'SubiT.spec')
icon_file_win32             = os.path.join(build_platform_helpers_path, 'subit-icon.ico')
win_associator_win32        = os.path.join(build_platform_helpers_path, 'WinAssociator')
manifest_file_base_win32    = os.path.join(build_platform_helpers_path, 'SubiT.exe.manifest')
setup_image_file_path_win32 = os.path.join(build_platform_helpers_path, 'subit-image-setup.bmp')
setup_logo_file_path_win32  = os.path.join(build_platform_helpers_path, 'subit-logo-setup.bmp')
setup_iss_file_path_win32   = os.path.join(build_platform_helpers_path, 'subit-template-setup.iss')

# The full path to the ISCC compiler. 
iscc_compiler_path = r'%programfiles%\Inno Setup 5\ISCC.exe'
iscc_compiler_path = os.path.expandvars(iscc_compiler_path)

def copyWinAssociatorDir(dest_dir):
    """ Will copy the files win32._helpers.WinAssociator to 
        dest_dir\Settings\Associators\WinAssociator.
    """
    log('Copying WinAssociator from [%s] to [%s]' % 
        (win_associator_win32, dest_dir))
    shutil.copytree(win_associator_win32, dest_dir)

def getWin32BinDirPath(debug):
    """ Returns the path for the release or debug binaries for win32. """
    return os.path.join(build_bin_path, getBuildStr(debug))

def getWin32ApplicationManifets():
    """ Get a win32 application manifest for subit. The manifest is returned as
        string to the caller.
    """
    _base_manifest = open(manifest_file_base_win32, 'r').read()
    return _base_manifest.format(subit_version = subit_version)

def getWin32SpecFile(tmp_path_for_build, build_path, manifest_path):
    """ Get the win32 .spec file for the current version of SubiT. The return
        value is a string containig the content.
    """
    _base_spec_content = open(spec_file_base_win32, 'r').read()
    return _base_spec_content.format(
        src_dir_path            = build_src_dir_path, 
        temp_dir_path           = tmp_path_for_build,
        final_build_dir_path    = build_path,
        helpers_dir_path        = build_platform_helpers_path,
        manifest_file_path      = manifest_path)
       
def getWin32IssFile(debug):
    """ Formats the ISS template for either debug or release setup. """
    _base_iss_content = open(setup_iss_file_path_win32, "r").read()
    return _base_iss_content.format(
        subit_version           = subit_version,
        setup_icon_file_path    = icon_file_win32,
        setup_logo_file_path    = setup_logo_file_path_win32,
        setup_image_file_path   = setup_image_file_path_win32,
        bin_dir_path            = getWin32BinDirPath(debug))

def zipWin32Dir(debug):
    """ 
        Zips the bin dir (debug or release). The archive's root will be the 
        bin dir.
    """
    import zipfile
    zip_name = zip_name_format_win32.format(build = getBuildStr(debug))
    zip_path = os.path.join(build_dist_path, zip_name)
    zip_file = zipfile.ZipFile(zip_path, "w")
    # The binary path to zip.
    bin_path = os.path.join(build_bin_path, getBuildStr(debug))
    for root, dirs, files in os.walk(bin_path):
        for file in files:
            # Remove the full path to the file, and keep only the relative.
            archive_name = root.replace(bin_path, "")
            archive_name = os.path.join(archive_name, file)
            zip_file.write(os.path.join(root, file), archive_name)
    zip_file.close()

def buildWin32Dir(debug):
    """ Build procedure for Windows. """

    _bin_path = getWin32BinDirPath(debug)
    _tmp_bin_path = os.path.join(build_bin_path, '__tmp_' + getBuildStr(debug))

    removeTreeAndWaitForFinish(_bin_path)
    removeTreeAndWaitForFinish(_tmp_bin_path)

    log('Creating _tmp_bin_path: %s' % _tmp_bin_path)
    os.mkdir(_tmp_bin_path)

    _manifest_path = os.path.join(_tmp_bin_path, subit_name + '.exe.manifest')
    open(_manifest_path, 'w').write(getWin32ApplicationManifets())

    _spec_path = os.path.join(_tmp_bin_path, subit_name + '.spec')
    _spec_content= getWin32SpecFile(_tmp_bin_path, _bin_path, _manifest_path)
    open(_spec_path, 'w').write(_spec_content)

    build_command = '"%s" "%s"' % (pyinstaller_build_path, _spec_path)
    build_output = executeInPythonInterpreter(build_command)
    for line in build_output.split("\n"):
        log('[Build.py] => %s' % line)

    log('Exe building finished: %s' % _bin_path)
    copySubProvidersFilesToDir(os.path.join(_bin_path, 'SubProviders'))
    copyWinAssociatorDir\
        (os.path.join(_bin_path, 'Settings', 'Associators', 'WinAssociator'))

def buildWin32Setup(debug):
    """ Creates the setup file of SubiT for win32 platform. """

    _setup_path = os.path.join(build_setup_path, getBuildStr(debug))
    removeTreeAndWaitForFinish(_setup_path)

    iss_for_version_path = os.path.join\
        (_setup_path, 'subit-%s-setup.iss' % subit_version)

    # Make sure the the iscc compiler is in place.
    if not os.path.exists(iscc_compiler_path):
        raise AttributeError(
            "The ISCC compiler is missing from: %s" % iscc_compiler_path)

    log('Creating new win32 setup folder: %s' % _setup_path)
    os.mkdir(_setup_path)

    iss_content = getWin32IssFile(debug)
    open(iss_for_version_path, 'w').write(iss_content)
    log('Inno Setup script created for current version: %s' % 
        iss_for_version_path)

    setup_file_name = 'subit-{subit_version}-setup-{build}-win32'.format(
       subit_version = subit_version, build = getBuildStr(debug))

    compiler_args = '"%s" /O"%s" /F%s' % \
        (iss_for_version_path, _setup_path, setup_file_name)
    compiler_full_command = '"%s" %s' % (iscc_compiler_path, compiler_args)
    log('Compiler params: %s' % compiler_full_command)

    for line in check_output(compiler_full_command).decode().split('\r\n'):
        log('[Compiler] => %s' % line)

    setup_file_name = setup_file_name + ".exe"

    # Copy to dist directory.
    shutil.copy(os.path.join(_setup_path, setup_file_name), build_dist_path)

    log('Setup compilation finished: %s' % _setup_path)
    
def buildWin32():
    """ Build the current version of SubiT out of the source code. Will create
        both the freezed version of SubiT (using PyInstaller) and also a setup
        file created by Inno Setup. 

        After calling this method, SubiT is ready to publish.
    """
    log('Starting build for SubiT %s for Win32 platform' % subit_version)

    # Clear the directories
    removeTreeAndWaitForFinish(build_bin_path)
    os.makedirs(build_bin_path)
    removeTreeAndWaitForFinish(build_setup_path)
    os.makedirs(build_setup_path)
    removeTreeAndWaitForFinish(build_dist_path)
    os.makedirs(build_dist_path)

    def _build_release():
        log('Building release version')
        copySrcDirToBuildDir()
        minifyPyFilesInSrc()
        reformatPythonFiles(False)
        buildWin32Dir(False)
        zipWin32Dir(False)
        buildWin32Setup(False)
        log('Finished building release version')
    def _build_debug():
        log('Building debug version')
        copySrcDirToBuildDir()
        reformatPythonFiles(True)
        buildWin32Dir(True)
        zipWin32Dir(True)
        buildWin32Setup(True)
        log('Finished building debug version')
    _build_release()
    _build_debug()

    copyReadmeToDist()

    log('Builing SubiT %s for win32 platform finished!' % subit_version)
# ============================================================================ #
# ============================================================================ #


if __name__ == '__main__':
    createAndMoveToTempBuildDir()
    if IsWindowsPlatform():
        buildWin32()
    else:
        raise NotImplementedError("Only Win32 compilation is supported!")
    log('================================FINISHED=============================')
    raw_input('Press any key to exit . . .')
