# VO Converter — Windows Portable ZIP build script
# Usage: .\build.ps1
# Requires: uv, PyInstaller (uv add --dev pyinstaller)

$ErrorActionPreference = 'Stop'
$AppName   = 'VO Converter'
$Version   = '0.1.0'
$OutZip    = "dist\VO_Converter_v${Version}_win64_portable.zip"

Write-Host "==> Cleaning previous build ..."
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

Write-Host "==> Running PyInstaller ..."
uv run pyinstaller vo_converter.spec
if (-not $?) { Write-Error "PyInstaller failed."; exit 1 }

Write-Host "==> Creating bin\ folder for ffmpeg ..."
New-Item -ItemType Directory -Path "dist\$AppName\bin" -Force | Out-Null

Write-Host "==> Packaging into ZIP (waiting for file locks to release) ..."
Start-Sleep -Seconds 5
Compress-Archive -Path "dist\$AppName" -DestinationPath $OutZip -Force

$size = [math]::Round((Get-Item $OutZip).Length / 1MB, 1)
Write-Host ""
Write-Host "Build complete: $OutZip ($size MB)"
Write-Host "Users can unzip and run '$AppName.exe' directly."
