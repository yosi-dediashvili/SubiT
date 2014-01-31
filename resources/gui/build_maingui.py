import os
import StringIO
from subprocess import check_output
from distutils.sysconfig import get_python_lib
from sys import prefix, executable

SUBIT_UI_DIR = os.path.dirname(__file__)
SUBIT_PY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(SUBIT_UI_DIR)), 
    "src", 
    "Interaction")
IMAGES_RESOURCES     = 'ImagesResources'
IMAGES_RESOURCES_PY  = os.path.join(SUBIT_PY_DIR, '%s.py' % IMAGES_RESOURCES)
IMAGES_RESOURCES_QRC = os.path.join(SUBIT_UI_DIR, 'images.qrc')

# Path to python's directory.
PYTHON_DIR = prefix
# Path to python's binary.
PYTHON_EXE = executable
PYSIDE_DIR = os.path.join(get_python_lib(), 'PySide')
UIC_PATH   = os.path.join(PYSIDE_DIR, 'scripts', 'uic.py')
RCC_PATH   = os.path.join(PYSIDE_DIR, 'pyside-rcc.exe' )

# Conversion between the ui files in the python files.
PATHS = ({'UI' : r'SubiTMainUi.ui',     'PY' : r'SubiTMainGui.py' },
         {'UI' : r'SubiTAboutUi.ui',    'PY' : r'SubiTAboutGui.py' },
         {'UI' : r'SubiTSettingsUi.ui', 'PY' : r'SubiTSettingsGui.py' },
         {'UI' : r'SubiTUpdateUi.ui',   'PY' : r'SubiTUpdateGui.py'},
         {'UI' : r'SubiTLanguageUi.ui', 'PY' : r'SubiTLanguageGui.py'})

if __name__ == '__main__':    
    for path in PATHS:
        ui_path = os.path.join(SUBIT_UI_DIR, path['UI'])
        py_path = os.path.join(SUBIT_PY_DIR, path['PY'])
        print('Working on ui: %s' % ui_path)
        output = check_output(
            '"%s" "%s" "%s"' % (PYTHON_EXE, UIC_PATH, ui_path), 
            universal_newlines=True).decode()
        output_lines = StringIO.StringIO(output).readlines()
        with open(py_path, 'w') as result_file:
            print('Created py: %s' % path['PY'])
            for line in output_lines:
                # Replace any import with our import.
                if 'import images_rc' in line:
                    line = line.replace(
                        'import images_rc', 
                        'from Interaction import %s' % IMAGES_RESOURCES)
                result_file.write(line)

    
    if os.path.exists(IMAGES_RESOURCES_PY):
        print('Old resource file exists, deleting it')
        os.remove(IMAGES_RESOURCES_PY)
        print('Old resource file deleted')

    print('Creating resource file at: %s'  % IMAGES_RESOURCES_PY)
    rcc_params = \
        r'"%s" -py2 -compress 9 -o "%s" "%s"' % \
        (RCC_PATH, IMAGES_RESOURCES_PY, IMAGES_RESOURCES_QRC)
    print('Calling pyside-rcc with: %s' % rcc_params)
    check_output(rcc_params, universal_newlines=True)
    print('pyside-rcc Called successfully!')
    print('Finished!')
    raw_input("Press any key to exit. . .")