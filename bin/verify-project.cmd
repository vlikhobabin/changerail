@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0verify-project" %*
exit /b %ERRORLEVEL%
