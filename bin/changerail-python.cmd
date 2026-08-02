@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "SELF_DIR=%~dp0"
for %%I in ("%SELF_DIR%..") do set "CHANGERAIL_ROOT=%%~fI"
set "WINDOWS_SELECTOR=%CHANGERAIL_ROOT%\scripts\changerail_python_windows.py"

if not exist "%WINDOWS_SELECTOR%" (
  echo ChangeRail Python runtime error: Windows selector helper is missing: %WINDOWS_SELECTOR% >&2
  exit /b 2
)

set "candidate_source=default"
set "candidate_args="
if defined CHANGERAIL_PYTHON (
  set "candidate=%CHANGERAIL_PYTHON%"
  set "candidate_source=CHANGERAIL_PYTHON"
  if "%CHANGERAIL_PYTHON%"=="" (
    echo ChangeRail Python runtime error: CHANGERAIL_PYTHON invalid: empty override; unset it or point it to Python 3.11 or newer. >&2
    exit /b 2
  )
  if not exist "%CHANGERAIL_PYTHON%" (
    where "%CHANGERAIL_PYTHON%" >nul 2>nul
    if errorlevel 1 (
      echo ChangeRail Python runtime error: CHANGERAIL_PYTHON invalid: interpreter '%CHANGERAIL_PYTHON%' was not found; unset it or point it to Python 3.11 or newer. >&2
      exit /b 2
    )
  )
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "candidate=python"
  ) else (
    where py >nul 2>nul
    if not errorlevel 1 (
      set "candidate=py"
      set "candidate_args=-3"
    ) else (
      echo ChangeRail Python runtime error: no Python interpreter found; install Python 3.11 or newer and runtime dependencies from requirements-runtime.txt, or set CHANGERAIL_PYTHON. >&2
      exit /b 2
    )
  )
)

"%candidate%" %candidate_args% "%WINDOWS_SELECTOR%" --source "%candidate_source%" --root "%CHANGERAIL_ROOT%" %*
exit /b %ERRORLEVEL%
