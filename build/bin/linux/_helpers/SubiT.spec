# -*- mode: python -*-
subit_analysis = Analysis(
	[r'{0}'],          # SubitProxy.py path
	pathex=[r'{1}'],   # __src path
	hiddenimports=[],
	hookspath=None)
subit_pyz = PYZ(subit_analysis.pure)

exe = EXE(
	subit_pyz,
	subit_analysis.scripts,
	exclude_binaries = 1,
	# full path to the new binary file (the .exe file in windows...)
	name=r'{2}',
	debug = False,
	strip = None)



coll_base = COLLECT(
	exe,
	subit_analysis.binaries,
	subit_analysis.zipfiles,
	subit_analysis.datas,
	strip=None,
	# The destination directory for the final build
	name=r'{3}')