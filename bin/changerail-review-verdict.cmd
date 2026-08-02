@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0changerail-review-verdict" %*
exit /b %ERRORLEVEL%
