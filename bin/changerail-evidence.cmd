@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0changerail-evidence" %*
exit /b %ERRORLEVEL%
