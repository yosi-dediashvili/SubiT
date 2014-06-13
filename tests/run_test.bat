:: Add the src directory to the python's path.
if "%PYTHONPATH%" == "" (
	set PYTHONPATH=%~dp0..\src
) else (
	set PYTHONPATH=%PYTHONPATH% + %~dp0..\src
)

:: Execute the script
python %~f1