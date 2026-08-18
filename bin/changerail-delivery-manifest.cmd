@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0changerail-delivery-manifest" %*
exit /b %ERRORLEVEL%
