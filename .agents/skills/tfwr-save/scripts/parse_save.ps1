[CmdletBinding()]
param(
    [string]$SavePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($SavePath)) {
    $SavePath = Join-Path $repoRoot 'Saves\Save0\save.json'
}
if (!(Test-Path -LiteralPath $SavePath -PathType Leaf)) {
    throw "Missing save: $SavePath"
}

$snapshotPath = Join-Path $PSScriptRoot '..\references\save-snapshot.md'
$catalogPath = Join-Path $PSScriptRoot '..\references\unlock-catalog.md'

$raw = [System.IO.File]::ReadAllText($SavePath)
$save = $raw | ConvertFrom-Json

$items = @()
if ($save.PSObject.Properties['items'] -and $save.items.PSObject.Properties['serializeList']) {
    foreach ($entry in @($save.items.serializeList)) {
        $items += [pscustomobject]@{
            Name  = [string]$entry.name
            Count = [double]$entry.nr
        }
    }
}

$unlockTokens = @()
if ($save.PSObject.Properties['unlocks']) {
    foreach ($token in @($save.unlocks)) {
        $unlockTokens += [string]$token
    }
}

$unlockSet = @{}
foreach ($token in $unlockTokens) {
    $unlockSet[$token.ToLowerInvariant()] = $true
}

function Test-HasToken {
    param([Parameter(Mandatory)][string[]]$Names)
    foreach ($name in $Names) {
        if ($unlockSet.ContainsKey($name.ToLowerInvariant())) {
            return $true
        }
    }
    return $false
}

$upgradeLevels = [ordered]@{}
$plainUnlocks = New-Object System.Collections.Generic.List[string]
foreach ($token in $unlockTokens) {
    if ($token -match '^(.*)_([0-9]+)$') {
        $prefix = $Matches[1]
        $level = [int]$Matches[2]
        if (-not $upgradeLevels.Contains($prefix)) {
            $upgradeLevels[$prefix] = $level
        }
        elseif ($level -gt $upgradeLevels[$prefix]) {
            $upgradeLevels[$prefix] = $level
        }
    }
    else {
        $plainUnlocks.Add($token)
    }
}

$lockedChecks = @(
    [pscustomobject]@{ Label = 'get_cost / Costs'; Tokens = @('costs', 'get_cost'); Safe = $false }
    [pscustomobject]@{ Label = 'unlock() / Auto_Unlock'; Tokens = @('auto_unlock', 'unlock'); Safe = $false }
    [pscustomobject]@{ Label = 'cactus / swap'; Tokens = @('cactus', 'swap'); Safe = $false }
    [pscustomobject]@{ Label = 'polyculture / get_companion'; Tokens = @('polyculture', 'get_companion'); Safe = $false }
    [pscustomobject]@{ Label = 'megafarm / spawn_drone'; Tokens = @('megafarm', 'spawn_drone', 'wait_for', 'has_finished'); Safe = $false }
    [pscustomobject]@{ Label = 'mazes / gold'; Tokens = @('mazes', 'maze', 'treasure', 'gold'); Safe = $false }
    [pscustomobject]@{ Label = 'dinosaurs'; Tokens = @('dinosaurs', 'dinosaur'); Safe = $false }
    [pscustomobject]@{ Label = 'debug_2 / set_world_size'; Tokens = @('debug_2', 'set_execution_speed', 'set_world_size'); Safe = $false }
    [pscustomobject]@{ Label = 'leaderboard'; Tokens = @('leaderboard', 'leaderboard_run'); Safe = $false }
    [pscustomobject]@{ Label = 'simulation'; Tokens = @('simulation', 'simulate'); Safe = $false }
    [pscustomobject]@{ Label = 'dictionaries'; Tokens = @('dictionaries', 'dict', 'dicts'); Safe = $false }
    [pscustomobject]@{ Label = 'utilities min/max/abs'; Tokens = @('utilities', 'min', 'max', 'abs'); Safe = $false }
    [pscustomobject]@{ Label = 'measure'; Tokens = @('measure'); Safe = $false }
    [pscustomobject]@{ Label = 'sunflowers'; Tokens = @('sunflowers', 'sunflower'); Safe = $false }
    [pscustomobject]@{ Label = 'pumpkins'; Tokens = @('pumpkins', 'pumpkin'); Safe = $false }
    [pscustomobject]@{ Label = 'carrots'; Tokens = @('carrots', 'carrot'); Safe = $false }
    [pscustomobject]@{ Label = 'trees'; Tokens = @('trees', 'tree'); Safe = $false }
    [pscustomobject]@{ Label = 'import / functions / lists'; Tokens = @('import', 'functions', 'lists'); Safe = $false }
)

foreach ($check in $lockedChecks) {
    $check.Safe = Test-HasToken -Names $check.Tokens
}

function Get-ItemCount {
    param([Parameter(Mandatory)][string]$Name)
    foreach ($item in $items) {
        if ($item.Name -eq $Name) {
            return $item.Count
        }
    }
    return 0
}

$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$version = 0
if ($save.PSObject.Properties['version']) {
    $version = $save.version
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('# Save0 snapshot')
$lines.Add('')
$lines.Add("Generated: $now")
$lines.Add("Source: ``Saves/Save0/save.json`` (version $version)")
$lines.Add('This file is overwritten by `parse_save.ps1`. Do not edit save.json from here.')
$lines.Add('')
$lines.Add('## Items')
$lines.Add('')
if ($items.Count -eq 0) {
    $lines.Add('- (empty serializeList)')
}
else {
    foreach ($item in $items) {
        $lines.Add(('- {0}: {1}' -f $item.Name, $item.Count))
    }
}
$lines.Add('')
$lines.Add('Missing from serializeList is treated as 0. Current carrot count: **' + (Get-ItemCount -Name 'carrot') + '**.')
$lines.Add('')
$lines.Add('## Upgrade levels')
$lines.Add('')
if ($upgradeLevels.Count -eq 0) {
    $lines.Add('- (none)')
}
else {
    foreach ($key in $upgradeLevels.Keys) {
        $lines.Add(('- `{0}`: {1}' -f $key, $upgradeLevels[$key]))
    }
}
$lines.Add('')
$lines.Add('Farm side length is `get_world_size()` at runtime. Do not hardcode 6 columns.')
$lines.Add('')
$lines.Add('## Feature flags vs drone APIs')
$lines.Add('')
foreach ($check in $lockedChecks) {
    $mark = 'locked'
    if ($check.Safe) {
        $mark = 'unlocked'
    }
    $lines.Add(('- {0}: **{1}**' -f $check.Label, $mark))
}
$lines.Add('')
$lines.Add('`unlocks` in the token list means `Unlocks` / `num_unlocked` only, not `unlock()`.')
$lines.Add('Do not call `trade` / seed item APIs even if those old tokens appear.')
$lines.Add('')
$lines.Add('## Raw unlock tokens')
$lines.Add('')
$lines.Add('```')
$lines.Add(($unlockTokens -join ', '))
$lines.Add('```')
$lines.Add('')
$lines.Add('See [unlock-catalog.md](unlock-catalog.md) for string-to-API mapping.')

$utf8 = New-Object System.Text.UTF8Encoding $false
$snapshotDir = Split-Path -Parent $snapshotPath
if (!(Test-Path -LiteralPath $snapshotDir)) {
    New-Item -ItemType Directory -Path $snapshotDir | Out-Null
}
[System.IO.File]::WriteAllText($snapshotPath, ($lines -join "`n") + "`n", $utf8)

Write-Host "Save: $SavePath"
Write-Host "Snapshot: $snapshotPath"
Write-Host ''
Write-Host ($lines -join "`n")

if (!(Test-Path -LiteralPath $catalogPath)) {
    Write-Host '[warn] unlock-catalog.md is missing'
}

exit 0
