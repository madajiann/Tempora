# Tempora installer for Windows.
# Copies bin\tempora.exe (or the repo-root tempora.exe) into
# %LOCALAPPDATA%\Programs\tempora and adds it to the user PATH.
# Usage: right-click -> Run with PowerShell, or: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
if (-not $repoRoot) { $repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }

$candidates = @(
    (Join-Path $repoRoot 'bin\tempora.exe'),
    (Join-Path $repoRoot 'tempora.exe')
)
$src = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $src) {
    Write-Error "tempora.exe not found. Build it first: go build -o bin\tempora.exe .\cmd\tempora"
}

$destDir = Join-Path $env:LOCALAPPDATA 'Programs\tempora'
New-Item -ItemType Directory -Force -Path $destDir | Out-Null
Copy-Item -Force $src (Join-Path $destDir 'tempora.exe')

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike "*$destDir*") {
    $newPath = if ([string]::IsNullOrEmpty($userPath)) { $destDir } else { "$userPath;$destDir" }
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
    Write-Host "Added $destDir to user PATH (reopen your terminal to take effect)."
}

Write-Host ""
Write-Host "Tempora installed: $destDir\tempora.exe"
& (Join-Path $destDir 'tempora.exe') --version
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Set a provider key, e.g. `$env:DEEPSEEK_API_KEY='sk-...' or `$env:GLM_API_KEY='...'  (see tempora setup)"
Write-Host "  2. Run:  tempora          (interactive TUI)"
Write-Host "           tempora -p ""task""   (one-shot print mode)"
Write-Host "Uninstall: delete $destDir and remove it from your user PATH."
