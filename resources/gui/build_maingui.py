import os
import StringIO
from subprocess import check_output


UI_DIR = os.path.dirname(__file__)
PY_DIR = r'D:\dev\SubiT\2.1.0\src\Interaction'
IMAGES_RESOURCES     = 'ImagesResources'
IMAGES_RESOURCES_PY  = os.path.join(PY_DIR, '%s.py' % IMAGES_RESOURCES)
IMAGES_RESOURCES_QRC = os.path.join(UI_DIR, 'images.qrc')

PYTHON_DIR = r'C:\Program Files (x86)\Python\Python27'
PYTHON_EXE = os.path.join(PYTHON_DIR, 'python.exe')
PYSIDE_DIR = os.path.join(PYTHON_DIR, r'Lib\site-packages\PySide')
UIC_PATH   = os.path.join(PYSIDE_DIR, r'scripts\uic.py')
RCC_PATH   = os.path.join(PYSIDE_DIR, 'pyside-rcc.exe' )

PATHS = ({'UI' : r'SubiTMainUi.ui',     'PY' : r'SubiTMainGui.py' },
         {'UI' : r'SubiTAboutUi.ui',    'PY' : r'SubiTAboutGui.py' },
         {'UI' : r'SubiTSettingsUi.ui', 'PY' : r'SubiTSettingsGui.py' },
         {'UI' : r'SubiTUpdateUi.ui',   'PY' : r'SubiTUpdateGui.py'},
         {'UI' : r'SubiTLanguageUi.ui', 'PY' : r'SubiTLanguageGui.py'})

if __name__ == '__main__':    
    for path in PATHS:
        ui_path = os.path.join(UI_DIR, path['UI'])
        py_path = os.path.join(PY_DIR, path['PY'])
        print('Working on ui: %s' % ui_path)
        p = check_output('"%s" "%s" "%s"' % (PYTHON_EXE, UIC_PATH, ui_path), universal_newlines=True).decode()
        lines = StringIO.StringIO(p).readlines()
        with open(py_path, 'w') as result_file:
            print('Created py: %s' % path['PY'])
            for line in lines:
                if 'import images_rc' in line:
                    line = line.replace('import images_rc', 'from Interaction import %s' % IMAGES_RESOURCES)
                result_file.write(line)

    
    if os.path.exists(IMAGES_RESOURCES_PY):
        print('Old resource file exists, deleting it')
        os.remove(IMAGES_RESOURCES_PY)
        print('Old resource file deleted')

    print('Creating resource file at: %s'  % IMAGES_RESOURCES_PY)
    rcc_params = r'"%s" -py2 -compress 9 -o "%s" "%s"' % (RCC_PATH, IMAGES_RESOURCES_PY, IMAGES_RESOURCES_QRC)
    print('Calling pyside-rcc with: %s' % rcc_params)
    check_output(rcc_params, universal_newlines=True)
    print('pyside-rcc Called successfully!')

    raw_input("Press any key to exit. . .")