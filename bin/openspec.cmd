@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "openspec_version=%OPENSPEC_VERSION%"
if not defined openspec_version set "openspec_version=1.3.1"

if not defined OPENSPEC_TELEMETRY set "OPENSPEC_TELEMETRY=0"
if not defined npm_config_prefer_offline set "npm_config_prefer_offline=true"

set "changed_dir="
if defined OPENSPEC_WORKDIR (
  pushd "%OPENSPEC_WORKDIR%"
  if errorlevel 1 exit /b 1
  set "changed_dir=1"
)

npx -y "@fission-ai/openspec@%openspec_version%" %*
set "status=%ERRORLEVEL%"

if defined changed_dir popd
exit /b %status%
