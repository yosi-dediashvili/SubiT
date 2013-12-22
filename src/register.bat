if EXIST "SubiT.exe" (goto:continue) else (echo not)
pause
goto:eof

:continue
set progloc = """%cd%\SubiT.exe""" ""%%1""
set progloc
for /f "tokens=3*" %%a in ('set progloc') do (reg add HKCR\*\shell\SubiT\command /ve /t REG_SZ /d "%%a %%b")
for /f "tokens=3*" %%a in ('set progloc') do (reg add HKCR\Folder\shell\SubiT\command /ve /t REG_SZ /d "%%a %%b")

pause