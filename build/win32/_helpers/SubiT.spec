from distutils.sysconfig import get_python_lib

src_dir_path    		= r'{src_dir_path}'
subitproxy_file_path 	= os.path.join(src_dir_path, "SubitProxy.py")
updater_file_path    	= os.path.join(src_dir_path, 
									   r"Settings\Updaters\WinUpdaterHelper.py")

temp_dir_path 			= r'{temp_dir_path}'
gui_exe_file_path    	= os.path.join(temp_dir_path, "SubiT.exe")
cli_exe_file_path    	= os.path.join(temp_dir_path, "SubiT-cli.exe")
update_exe_file_path 	= os.path.join(temp_dir_path, 
									   r"Settings\Updaters\SubiT-updater.exe")

final_build_dir_path 	= r'{final_build_dir_path}'
helpers_dir_path    	= r'{helpers_dir_path}'
icon_file_path       	= os.path.join(helpers_dir_path, "subit-icon.ico")

manifest_file_path 		= r'{manifest_file_path}'

subit_analysis = Analysis(
	[subitproxy_file_path],          
	pathex=[src_dir_path],
	hiddenimports=[],
	hookspath=None)
subit_pyz = PYZ(subit_analysis.pure)

update_analysis = Analysis(
	[updater_file_path],          
	pathex=[src_dir_path],
	hiddenimports=[],
	excludes =['PySide'],
	hookspath=None)
update_pyz = PYZ(update_analysis.pure)

exe_windowed = EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	name=gui_exe_file_path,
	debug = False,
	strip = None,
	upx = True,
	console = False,
	icon=icon_file_path,
	manifest=manifest_file_path)

exe_console =  EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	name=cli_exe_file_path,
	debug = False,
	strip = None,
	upx = True,
	console = True,
	icon=icon_file_path,
	manifest=manifest_file_path)

exe_update = EXE(
	update_pyz,
	update_analysis.scripts,
	exclude_binaries = 1,
	name=update_exe_file_path,
	debug = False,
	strip = None,
	upx = True,
	console = True,
	icon=icon_file_path)

coll_base = COLLECT(
	exe_windowed,
	exe_console,
	subit_analysis.binaries,
	subit_analysis.zipfiles,
	subit_analysis.datas,
	strip=None,
	upx=True,
	name=final_build_dir_path)

coll_updater = COLLECT(
	exe_update, 
	update_analysis.binaries,
	update_analysis.zipfiles,
	update_analysis.datas,
	strip=None,
	upx=True,
	name=os.path.join(final_build_dir_path, 'Settings', 'Updaters'))


coll_gif = COLLECT(
	[(	
		'qgif4.dll', 
		os.path.join(
			get_python_lib(), 
			r"PySide\plugins\imageformats\qgif4.dll"), 
		'BINARY')],
	upx = False,
	strip = None,
	name = os.path.join(final_build_dir_path, 'imageformats'))