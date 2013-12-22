# -*- mode: python -*-
subit_analysis = Analysis(
	[r'{0}'],          # SubitProxy.py path
	pathex=[r'{1}'],   # __src path
	hiddenimports=[],
	hookspath=None)
subit_pyz = PYZ(subit_analysis.pure)

update_analysis = Analysis(
	[r'{0}'.replace('SubiTProxy.py', 'Settings\\Updaters\\WinUpdaterHelper.py')],          
	pathex=[r'{1}'],   # __src path
	hiddenimports=[],
	excludes =['PySide'],
	hookspath=None)
update_pyz = PYZ(update_analysis.pure)

exe_windowed = EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=r'{2}',
	debug = False,
	strip = None,
	upx = True,
	console = False,
	# Path to the icon file
	icon=r'{5}',
	# Path to the manifest file
	manifest=r'{6}')

exe_console =  EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=r'{3}',
	debug = False,
	strip = None,
	upx = True,
	console = True,
	# Path to the icon file
	icon=r'{5}',
	# Path to the manifest file
	manifest=r'{6}')

exe_update = EXE(
	update_pyz,
	update_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=r'{4}',
	debug = False,
	strip = None,
	upx = True,
	console = True,
	# Path to the icon file
	icon=r'{5}')

coll_base = COLLECT(
	exe_windowed,
	exe_console,
	subit_analysis.binaries,
	subit_analysis.zipfiles,
	subit_analysis.datas,
	strip=None,
	upx=True,
	# The destination directory for the final build
	name=r'{7}')

coll_updater = COLLECT(
	exe_update, 
	update_analysis.binaries,
	update_analysis.zipfiles,
	update_analysis.datas,
	strip=None,
	upx=True,
	# The destination directory for the final build
	name=os.path.join(r'{7}', 'Settings', 'Updaters'))

coll_gif = COLLECT(
	[('qgif4.dll', r'C:\\Program Files (x86)\\Python\\Python27\\Lib\site-packages\\PySide\\plugins\\imageformats\\qgif4.dll', 'BINARY')],
	upx = False,
	strip = None,
	name = os.path.join(r'{7}', 'imageformats'))