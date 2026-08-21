@echo off
setlocal EnableExtensions DisableDelayedExpansion

call "%~dp0changerail-python.cmd" "%~dp0..\scripts\changerail_source_classification.py" %*
exit /b %ERRORLEVEL%
