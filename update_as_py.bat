@echo off

:start
cls

set python_ver=36

py ./src/get-pip.py
IF ERRORLEVEL 1 (
  echo Failed to install pip.
  goto ERROR
)

py -m pip install -r requirements.txt
IF ERRORLEVEL 1 (
  echo Failed to install requirements.
  goto ERROR
)

py src/updater.py
IF ERRORLEVEL 1 (
  echo Failed to run updater.py.
  goto ERROR
)

pause
exit

:ERROR
echo An error occurred. Check the above messages for more details.
pause
exit /b 1
