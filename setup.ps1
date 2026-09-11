# Copy this repo into the game save folder, then finish init (skills links + farm scripts).
[CmdletBinding()]
param(
    [string]$GameRoot,
    [switch]$SkipFarmScripts,
    [switch]$ExportFarm,
    [switch]$NonInteractive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Get-Location).Path
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

function Normalize-PathInput {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ''
    }
    $text = $Value.Trim()
    $text = $text.Trim('"')
    $text = $text.Trim("'")
    $text = $text.TrimEnd('\')
    return $text
}

function Read-SavePath {
    $default = Join-Path $env:USERPROFILE 'AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced'
    if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
        return (Normalize-PathInput $GameRoot)
    }
    if ($NonInteractive) {
        return $default
    }
    Write-Host ''
    Write-Host 'Enter the game SAVE folder, not the Steam install folder.'
    Write-Host ''
    Write-Host 'Default (press Enter):'
    Write-Host "  $default"
    Write-Host ''
    Write-Host 'Hint: launch the game once so this folder exists. Do not use steamapps\common\...'
    $typed = Read-Host 'Save path'
    $typed = Normalize-PathInput $typed
    if ([string]::IsNullOrWhiteSpace($typed)) {
        return $default
    }
    return $typed
}

function Assert-SaveFolder {
    param([Parameter(Mandatory)][string]$Path)
    if ($Path -match 'steamapps\\common') {
        throw "This is the Steam install folder, not the save folder.`nExpected something like: $env:USERPROFILE\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced"
    }
    if (!(Test-Path -LiteralPath $Path -PathType Container)) {
        throw "Folder not found: $Path`nLaunch the game once so the save folder exists, or check the path."
    }
    return (Resolve-Path -LiteralPath $Path).Path
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
    if (Test-Path -LiteralPath $To) {
        Remove-Item -LiteralPath $To -Recurse -Force
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

function Copy-WorkspaceIntoSave {
    param(
        [Parameter(Mandatory)][string]$From,
        [Parameter(Mandatory)][string]$To
    )
    $names = @(
        'AGENTS.md',
        'options.example.txt',
        'setup.bat',
        'setup.ps1',
        '.gitignore',
        '.gitattributes'
    )
    foreach ($name in $names) {
        $src = Join-Path $From $name
        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $To $name) -Force
        }
    }
    Get-ChildItem -LiteralPath $From -Filter 'README*.md' -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $To $_.Name) -Force
    }
    $skillsSrc = Join-Path $From '.agents\skills'
    if (!(Test-Path -LiteralPath $skillsSrc)) {
        throw "Missing canonical skills: $skillsSrc"
    }
    $agentsDst = Join-Path $To '.agents'
    if (!(Test-Path -LiteralPath $agentsDst)) {
        New-Item -ItemType Directory -Path $agentsDst | Out-Null
    }
    Copy-Tree -From $skillsSrc -To (Join-Path $To '.agents\skills')
    $templatesSrc = Join-Path $From 'templates'
    if (Test-Path -LiteralPath $templatesSrc) {
        Copy-Tree -From $templatesSrc -To (Join-Path $To 'templates')
    }
    Write-Host '[ok] Copied workspace into the save folder. save.json was not touched.'
}

function Install-AgentLinks {
    param([Parameter(Mandatory)][string]$Dest)
    $linkScript = Join-Path $Dest '.agents\skills\tfwr-farm\scripts\ensure-agent-links.ps1'
    if (!(Test-Path -LiteralPath $linkScript)) {
        throw "Missing link script: $linkScript"
    }
    & $linkScript
    if ($LASTEXITCODE -ne 0) {
        throw "ensure-agent-links failed with exit $LASTEXITCODE"
    }
}

$templateDir = Join-Path $RepoRoot 'templates\Save0'

if ($ExportFarm) {
    $exportRoot = if ([string]::IsNullOrWhiteSpace($GameRoot)) { $RepoRoot } else { (Assert-SaveFolder (Normalize-PathInput $GameRoot)) }
    $saveDir = Join-Path $exportRoot 'Saves\Save0'
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

$dest = Assert-SaveFolder (Read-SavePath)
Write-Host "Repo: $RepoRoot"
Write-Host "Save: $dest"

if ($RepoRoot -ne $dest) {
    Write-Host '[copy] Copying this repo into the save folder...'
    Copy-WorkspaceIntoSave -From $RepoRoot -To $dest
}
else {
    Write-Host '[skip] Already inside the save folder; no copy needed.'
}

$workRoot = $dest
$templateAtDest = Join-Path $workRoot 'templates\Save0'
if (Test-Path -LiteralPath $templateAtDest) {
    $templateDir = $templateAtDest
}

if (-not $SkipFarmScripts) {
    if (Test-Path -LiteralPath $templateDir) {
        Copy-FarmScripts -FromDir $templateDir -ToDir (Join-Path $workRoot 'Saves\Save0')
        Write-Host '[ok] Farm scripts installed into Saves\Save0 (save.json left alone).'
        Write-Host '     New .py files still need a same-name window in the in-game editor.'
    }
    else {
        Write-Host '[skip] templates\Save0 is missing; farm scripts not copied.'
    }
}

Write-Host '[init] Creating Claude / Cursor / Grok skill links...'
Install-AgentLinks -Dest $workRoot

Write-Host ''
Write-Host 'Init finished by itself.'
Write-Host "Open this folder in Cursor: $workRoot"
Write-Host 'Then:'
Write-Host '  python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main'
Write-Host 'Do not press F5. Do not run the farm with main_maze.'
exit 0
