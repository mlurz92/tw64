$ErrorActionPreference='Stop'
$Root = Split-Path -Parent $PSScriptRoot
$ReleaseRoot = (Resolve-Path (Join-Path $Root 'dist\release-root')).Path
$Out = Join-Path $Root 'dist\AssemblyNetStudio-1.0.0-x64.msi'
$ToolDir = Join-Path $Root '.tools\wix'
New-Item -ItemType Directory -Force $ToolDir | Out-Null
if (-not (Test-Path (Join-Path $ToolDir 'wix.exe'))) { dotnet tool install wix --version 5.0.2 --tool-path $ToolDir }
& (Join-Path $ToolDir 'wix.exe') build (Join-Path $Root 'installer\Product.wxs') -arch x64 -d "ReleaseRoot=$ReleaseRoot" -out $Out
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Out)) { throw 'WiX MSI build failed.' }
(Get-FileHash -Algorithm SHA256 $Out).Hash.ToLowerInvariant() + '  ' + (Split-Path -Leaf $Out) | Set-Content -Encoding ascii (Join-Path $Root 'dist\SHA256SUMS')
Write-Host "Built $Out"
