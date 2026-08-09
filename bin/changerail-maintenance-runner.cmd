@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0changerail-maintenance-runner" %*
exit /b %ERRORLEVEL%
