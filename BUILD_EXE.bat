@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul
set "PYTHONUTF8=1"
title Minecraft Translator - build EXE

echo ============================================================
echo   Minecraft Translator - one-click EXE builder
echo ============================================================
echo.

set "PY="
for %%V in (3.12 3.13 3.11 3.10) do (
  if not defined PY (
    py -%%V -c "import sys" >nul 2>nul && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,13) else 1)" >nul 2>nul && set "PY=python"
)

if not defined PY (
  echo Python 3.10 - 3.13 was not found on this computer.
  where winget >nul 2>nul
  if not errorlevel 1 (
    echo.
    choice /m "Install Python 3.12 automatically with winget"
    if not errorlevel 2 (
      winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
      echo.
      echo Python was installed. CLOSE this window and run BUILD_EXE.bat again.
      pause
      exit /b 0
    )
  )
  echo.
  echo Install Python 3.12 x64 from https://www.python.org/downloads/
  echo On the first screen tick "Add python.exe to PATH", then run BUILD_EXE.bat again.
  pause
  exit /b 1
)

echo Using Python: %PY%
%PY% --version

set "VENV=%CD%\.build_venv"
if not exist "%VENV%\Scripts\python.exe" (
  echo.
  echo Creating isolated build environment ^(one time only^)...
  %PY% -m venv "%VENV%"
  if errorlevel 1 goto :fail
)
set "VPY=%VENV%\Scripts\python.exe"

echo.
echo Installing / checking libraries...
"%VPY%" -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 goto :fail
"%VPY%" -m pip install --disable-pip-version-check -r requirements.txt pyinstaller
if errorlevel 1 goto :fail

"%VPY%" build_exe.py %*
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   DONE. The ready program is in the "dist" folder:
echo   dist\MinecraftTranslator.exe
echo   Just run it - nothing else is needed on the target PC.
echo ============================================================
if exist "dist\MinecraftTranslator.exe" explorer "dist"
pause
exit /b 0

:fail
echo.
echo ============================================================
echo   BUILD FAILED. Read the message above.
echo   Typical fixes: check internet, pause the antivirus, run again.
echo ============================================================
pause
exit /b 1
