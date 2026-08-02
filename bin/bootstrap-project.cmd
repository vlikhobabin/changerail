@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0bootstrap-project" %*
exit /b %ERRORLEVEL%
