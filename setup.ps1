# One-shot install: copy canonical skills + farm templates into the TFWR userdata folder.
[CmdletBinding()]
param(
    [string]$GameRoot,
    [switch]$SkipFarmScripts,
    [switch]$ExportFarm
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Get-Location).Path
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

function Find-GameRoot {
    if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
        return (Resolve-Path -LiteralPath $GameRoot).Path
    }
    $default = Join-Path $env:USERPROFILE 'AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced'
    $markers = @(
        (Join-Path $RepoRoot 'Saves\Save0'),
        (Join-Path $RepoRoot 'AGENTS.md')
    )
    if ((Test-Path -LiteralPath $markers[0]) -or (Test-Path -LiteralPath $markers[1])) {
        if (Test-Path -LiteralPath $default) {
            $defaultFull = (Resolve-Path -LiteralPath $default).Path
            if ($defaultFull -eq $RepoRoot) {
                return $RepoRoot
            }
        }
        if (Test-Path -LiteralPath (Join-Path $RepoRoot 'Saves\Save0')) {
            return $RepoRoot
        }
    }
    if (Test-Path -LiteralPath $default) {
        return (Resolve-Path -LiteralPath $default).Path
    }
    throw "Cannot find the game folder. Pass -GameRoot `"$default`""
}

function Copy-Tree {
    param(
        [Parameter(Mandatory)][string]$From,
        [Parameter(Mandatory)][string]$To
    )
    if (!(Test-Path -LiteralPath $From)) {
        throw "Missing source: $From"
    }
    $parent = Split-Path -Parent $To
    if ($parent -and !(Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    Copy-Item -LiteralPath $From -Destination $To -Recurse -Force
}

function Copy-FarmScripts {
    param(
        [Parameter(Mandatory)][string]$FromDir,
        [Parameter(Mandatory)][string]$ToDir
    )
    if (!(Test-Path -LiteralPath $FromDir)) {
        throw "Missing farm scripts: $FromDir"
    }
    if (!(Test-Path -LiteralPath $ToDir)) {
        New-Item -ItemType Directory -Path $ToDir -Force | Out-Null
    }
    Get-ChildItem -LiteralPath $FromDir -Filter '*.py' -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $ToDir $_.Name) -Force
        Write-Host "[farm] $($_.Name)"
    }
}

$dest = Find-GameRoot
Write-Host "Repo: $RepoRoot"
Write-Host "Game: $dest"

$templateDir = Join-Path $RepoRoot 'templates\Save0'
$saveDir = Join-Path $dest 'Saves\Save0'

if ($ExportFarm) {
    if (!(Test-Path -LiteralPath $saveDir)) {
        throw "No Saves\Save0 to export: $saveDir"
    }
    if (!(Test-Path -LiteralPath $templateDir)) {
        New-Item -ItemType Directory -Path $templateDir -Force | Out-Null
    }
    Copy-FarmScripts -FromDir $saveDir -ToDir $templateDir
    Write-Host '[ok] Exported Saves\Save0\*.py to templates\Save0. save.json was not copied.'
    exit 0
}

$sameRoot = $RepoRoot -eq $dest
if (-not $sameRoot) {
    Copy-Item -LiteralPath (Join-Path $RepoRoot 'AGENTS.md') -Destination (Join-Path $dest 'AGENTS.md') -Force
    $skillsSrc = Join-Path $RepoRoot '.agents\skills'
    $skillsDst = Join-Path $dest '.agents\skills'
    if (!(Test-Path -LiteralPath $skillsSrc)) {
        throw "Missing canonical skills: $skillsSrc"
    }
    if (Test-Path -LiteralPath $skillsDst) {
        Remove-Item -LiteralPath $skillsDst -Recurse -Force
    }
    $agentsDst = Join-Path $dest '.agents'
    if (!(Test-Path -LiteralPath $agentsDst)) {
        New-Item -ItemType Directory -Path $agentsDst | Out-Null
    }
    Copy-Tree -From $skillsSrc -To $skillsDst
    Write-Host '[ok] Copied AGENTS.md and .agents\skills'
}

if (-not $SkipFarmScripts) {
    if (Test-Path -LiteralPath $templateDir) {
        Copy-FarmScripts -FromDir $templateDir -ToDir $saveDir
        Write-Host '[ok] Farm scripts copied into Saves\Save0 (save.json left alone).'
        Write-Host '     New .py files still need a same-name window in the in-game editor.'
    }
    else {
        Write-Host '[skip] templates\Save0 is missing; farm scripts not copied.'
    }
}

$linkScript = Join-Path $dest '.agents\skills\tfwr-farm\scripts\ensure-agent-links.ps1'
if (!(Test-Path -LiteralPath $linkScript)) {
    throw "Missing link script: $linkScript"
}
& $linkScript
if ($LASTEXITCODE -ne 0) {
    throw "ensure-agent-links failed with exit $LASTEXITCODE"
}

Write-Host ''
Write-Host 'Next:'
Write-Host "  1. Open this folder in Cursor: $dest"
Write-Host '  2. Enable file watcher in the game (see options.example.txt).'
Write-Host '  3. Start the farm with:'
Write-Host '     python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main'
Write-Host '     Do not press F5. Do not run main_maze for the farm.'
exit 0
