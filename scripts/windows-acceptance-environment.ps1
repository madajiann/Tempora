# Match the production package smoke environment: inherited Tempora overrides
# must not redirect state/cache writes or enable a development-only launch.
function Get-WindowsAcceptanceEnvironment {
  $snapshot = @{}
  foreach ($entry in Get-ChildItem Env:) {
    if ($entry.Name -match '^TEMPORA_|^(NODE_OPTIONS|ELECTRON_RUN_AS_NODE)$') {
      $snapshot[$entry.Name] = $entry.Value
    }
  }
  return $snapshot
}

function Restore-WindowsAcceptanceEnvironment {
  param([hashtable]$Snapshot)
  foreach ($key in (Get-WindowsAcceptanceEnvironment).Keys) {
    [Environment]::SetEnvironmentVariable($key, $null, 'Process')
  }
  foreach ($key in $Snapshot.Keys) {
    [Environment]::SetEnvironmentVariable($key, $Snapshot[$key], 'Process')
  }
}

function Enter-WindowsAcceptanceEnvironment {
  param([Parameter(Mandatory=$true)][string]$DataHome)
  $snapshot = Get-WindowsAcceptanceEnvironment
  try {
    foreach ($key in $snapshot.Keys) {
      [Environment]::SetEnvironmentVariable($key, $null, 'Process')
    }
    $env:TEMPORA_HOME = [IO.Path]::GetFullPath($DataHome)
    $env:TEMPORA_STATE_HOME = $env:TEMPORA_HOME
    $env:TEMPORA_CACHE_HOME = Join-Path $env:TEMPORA_HOME 'cache'
    $env:TEMPORA_NONINTERACTIVE = '1'
    return $snapshot
  } catch {
    Restore-WindowsAcceptanceEnvironment -Snapshot $snapshot
    throw
  }
}
