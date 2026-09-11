# Copy this repo into the game save folder, then finish init (skills links + farm scripts).
[CmdletBinding()]
param(
    [string]$GameRoot,
    [string]$Lang,
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
$I18nDir = Join-Path $RepoRoot 'i18n'

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

function Read-JsonFile {
    param([Parameter(Mandatory)][string]$Path)
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Resolve-Lang {
    param([string]$Value)
    $raw = if ($null -eq $Value) { '' } else { $Value.Trim() }
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return 'en'
    }
    $catalogPath = Join-Path $I18nDir 'languages.json'
    if (Test-Path -LiteralPath $catalogPath) {
        $catalog = Read-JsonFile $catalogPath
        foreach ($entry in $catalog.languages) {
            if ($entry.id -eq $raw) {
                return $entry.id
            }
            foreach ($alias in $entry.aliases) {
                if ([string]::Equals($alias, $raw, [System.StringComparison]::OrdinalIgnoreCase)) {
                    return $entry.id
                }
            }
        }
    }
    $direct = Join-Path $I18nDir ("setup.$raw.json")
    if (Test-Path -LiteralPath $direct) {
        return $raw
    }
    return ''
}

function Import-Messages {
    param([string]$LangId)
    $enPath = Join-Path $I18nDir 'setup.en.json'
    if (!(Test-Path -LiteralPath $enPath)) {
        throw "Missing English setup strings: $enPath"
    }
    $script:MsgEn = Read-JsonFile $enPath
    $script:Msg = $script:MsgEn
    if ([string]::IsNullOrWhiteSpace($LangId) -or $LangId -eq 'en') {
        return
    }
    $path = Join-Path $I18nDir ("setup.$LangId.json")
    if (Test-Path -LiteralPath $path) {
        $script:Msg = Read-JsonFile $path
    }
}

function Get-MessageText {
    param(
        $Bag,
        [string]$Key
    )
    if ($null -eq $Bag) {
        return $null
    }
    $prop = $Bag.PSObject.Properties[$Key]
    if ($null -eq $prop) {
        return $null
    }
    return [string]$prop.Value
}

function T {
    param(
        [Parameter(Mandatory)][string]$Key,
        [object[]]$FormatArgs
    )
    $text = Get-MessageText -Bag $script:Msg -Key $Key
    if ([string]::IsNullOrEmpty($text)) {
        $text = Get-MessageText -Bag $script:MsgEn -Key $Key
    }
    if ([string]::IsNullOrEmpty($text)) {
        $text = $Key
    }
    if ($FormatArgs -and $FormatArgs.Count -gt 0) {
        return [string]::Format($text, $FormatArgs)
    }
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
    Write-Host (T 'enter_save')
    Write-Host ''
    Write-Host (T 'default_label')
    Write-Host "  $default"
    Write-Host ''
    Write-Host (T 'hints_title')
    Write-Host ("  - " + (T 'hint_launch'))
    Write-Host ("  - " + (T 'hint_steam'))
    Write-Host ("  - " + (T 'hint_paste'))
    Write-Host ("  - " + (T 'hint_auto'))
    Write-Host ''
    $typed = Read-Host (T 'save_path_prompt')
    $typed = Normalize-PathInput $typed
    if ([string]::IsNullOrWhiteSpace($typed)) {
        return $default
    }
    return $typed
}

function Assert-SaveFolder {
    param([Parameter(Mandatory)][string]$Path)
    $expected = Join-Path $env:USERPROFILE 'AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced'
    if ($Path -match 'steamapps\\common') {
        throw (T 'steam_error' @($expected))
    }
    if (!(Test-Path -LiteralPath $Path -PathType Container)) {
        throw (T 'missing_folder' @($Path))
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
    foreach ($folder in @('templates', 'i18n')) {
        $src = Join-Path $From $folder
        if (Test-Path -LiteralPath $src) {
            Copy-Tree -From $src -To (Join-Path $To $folder)
        }
    }
    Write-Host (T 'copied_ok')
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

$requestedLang = $Lang
$resolvedLang = Resolve-Lang $Lang
if ([string]::IsNullOrWhiteSpace($resolvedLang)) {
    Import-Messages 'en'
    Write-Host (T 'lang_fallback' @($requestedLang))
    $resolvedLang = 'en'
}
else {
    Import-Messages $resolvedLang
}

$templateDir = Join-Path $RepoRoot 'templates\Save0'

try {
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
        Write-Host (T 'export_ok')
        exit 0
    }

    Write-Host (T 'title')
    $dest = Assert-SaveFolder (Read-SavePath)
    Write-Host "$(T 'repo'): $RepoRoot"
    Write-Host "$(T 'save'): $dest"
    Write-Host "$(T 'target'): $dest"
    Write-Host (T 'copying')

    if ($RepoRoot -ne $dest) {
        Write-Host (T 'copying_repo')
        Copy-WorkspaceIntoSave -From $RepoRoot -To $dest
    }
    else {
        Write-Host (T 'already_inside')
    }

    $workRoot = $dest
    $templateAtDest = Join-Path $workRoot 'templates\Save0'
    if (Test-Path -LiteralPath $templateAtDest) {
        $templateDir = $templateAtDest
    }

    if (-not $SkipFarmScripts) {
        if (Test-Path -LiteralPath $templateDir) {
            Copy-FarmScripts -FromDir $templateDir -ToDir (Join-Path $workRoot 'Saves\Save0')
            Write-Host (T 'farm_ok')
            Write-Host (T 'farm_need_window')
        }
        else {
            Write-Host (T 'farm_skip')
        }
    }

    Write-Host (T 'init_links')
    Install-AgentLinks -Dest $workRoot

    Write-Host ''
    Write-Host (T 'done')
    Write-Host (T 'init_done')
    Write-Host (T 'open_cursor' @($workRoot))
    Write-Host (T 'next')
    Write-Host ("  1. " + (T 'next_1'))
    Write-Host ("  2. " + (T 'next_2'))
    Write-Host ("  3. " + (T 'next_3'))
    Write-Host (T 'no_f5')
    exit 0
}
catch {
    Write-Host $_.Exception.Message
    Write-Host (T 'fail')
    exit 1
}
