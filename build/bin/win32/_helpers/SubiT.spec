from distutils.sysconfig import get_python_lib

src_dir_path    = r'{0}'
subitproxy_path = os.path.join(src_dir_path, "SubitProxy.py")
updater_path    = os.path.join(src_dir_path, 
							   r"Settings\Updaters\WinUpdaterHelper.py")

temp_build_path = r'{1}'
gui_exe_path    = os.path.join(temp_build_path, "SubiT.exe")
cli_exe_path    = os.path.join(temp_build_path, "SubiT-cli.exe")
update_exe_path = os.path.join(temp_build_path, 
							   r"Settings\Updaters\SubiT-updater.exe")

final_build_path = r'{2}'

helpers_path    = r'{3}'
icon_path       = os.path.join(helpers_path, "icon.ico")

manifest_path   = r'{4}'

subit_analysis = Analysis(
	[subitproxy_path],          # SubitProxy.py path
	pathex=[src_dir_path],   # __src path
	hiddenimports=[],
	hookspath=None)
subit_pyz = PYZ(subit_analysis.pure)

update_analysis = Analysis(
	[updater_path],          
	pathex=[src_dir_path],   # __src path
	hiddenimports=[],
	excludes =['PySide'],
	hookspath=None)
update_pyz = PYZ(update_analysis.pure)

exe_windowed = EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=gui_exe_path,
	debug = False,
	strip = None,
	upx = True,
	console = False,
	# Path to the icon file
	icon=icon_path,
	# Path to the manifest file
	manifest=manifest_path)

exe_console =  EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=cli_exe_path,
	debug = False,
	strip = None,
	upx = True,
	console = True,
	# Path to the icon file
	icon=icon_path,
	# Path to the manifest file
	manifest=manifest_path)

exe_update = EXE(
	update_pyz,
	update_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=update_exe_path,
	debug = False,
	strip = None,
	upx = True,
	console = True,
	# Path to the icon file
	icon=icon_path)

coll_base = COLLECT(
	exe_windowed,
	exe_console,
	subit_analysis.binaries,
	subit_analysis.zipfiles,
	subit_analysis.datas,
	strip=None,
	upx=True,
	# The destination directory for the final build
	name=final_build_path)

coll_updater = COLLECT(
	exe_update, 
	update_analysis.binaries,
	update_analysis.zipfiles,
	update_analysis.datas,
	strip=None,
	upx=True,
	# The destination directory for the final build
	name=os.path.join(final_build_path, 'Settings', 'Updaters'))


coll_gif = COLLECT(
	[(	
		'qgif4.dll', 
		os.path.join(
			get_python_lib(), 
			r"PySide\plugins\imageformats\qgif4.dll"), 
		'BINARY')],
	upx = False,
	strip = None,
	name = os.path.join(final_build_path, 'imageformats'))