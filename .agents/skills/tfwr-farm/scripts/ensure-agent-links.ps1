[CmdletBinding()]
param(
    [switch]$CheckOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
Set-Location -LiteralPath $repoRoot

function Get-LinkInfo {
    param([Parameter(Mandatory)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{
            Exists   = $false
            IsLink   = $false
            Target   = $null
            PathType = $null
        }
    }

    $item = Get-Item -LiteralPath $Path -Force
    $isLink = $false
    $target = $null
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        $isLink = $true
        if ($item.PSObject.Properties['Target'] -and $item.Target) {
            $target = @($item.Target)[0]
        }
    }

    $pathType = if ($item.PSIsContainer) { 'Directory' } else { 'File' }
    return [pscustomobject]@{
        Exists   = $true
        IsLink   = $isLink
        Target   = $target
        PathType = $pathType
    }
}

function Test-TargetEquals {
    param(
        [string]$Actual,
        [Parameter(Mandatory)][string]$Expected
    )

    if ([string]::IsNullOrWhiteSpace($Actual)) {
        return $false
    }

    $normalize = {
        param($value)
        return ($value -replace '/', '\').TrimEnd('\').ToLowerInvariant()
    }

    return (& $normalize $Actual) -eq (& $normalize $Expected)
}

function New-RelativeLink {
    param(
        [Parameter(Mandatory)][string]$LinkPath,
        [Parameter(Mandatory)][string]$Target,
        [Parameter(Mandatory)][ValidateSet('Directory', 'File')][string]$Kind
    )

    $parent = Split-Path -Parent $LinkPath
    if ($parent -and !(Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }

    $quotedLink = '"' + $LinkPath + '"'
    $quotedTarget = '"' + $Target + '"'
    if ($Kind -eq 'Directory') {
        $null = cmd /c "mklink /D $quotedLink $quotedTarget"
    }
    else {
        $null = cmd /c "mklink $quotedLink $quotedTarget"
    }

    if ($LASTEXITCODE -ne 0) {
        throw "mklink failed: $LinkPath -> $Target. Enable Windows Developer Mode and retry."
    }
}

$agentsMd = Join-Path $repoRoot 'AGENTS.md'
$skillsDir = Join-Path $repoRoot '.agents\skills'
if (!(Test-Path -LiteralPath $agentsMd -PathType Leaf)) {
    throw "Missing AGENTS.md: $agentsMd"
}
if (!(Test-Path -LiteralPath $skillsDir -PathType Container)) {
    throw "Missing .agents\skills: $skillsDir"
}

$specs = @(
    [pscustomobject]@{ Path = '.claude\skills'; Target = '..\.agents\skills'; Kind = 'Directory' }
    [pscustomobject]@{ Path = '.grok\skills'; Target = '..\.agents\skills'; Kind = 'Directory' }
    [pscustomobject]@{ Path = '.cursor\skills'; Target = '..\.agents\skills'; Kind = 'Directory' }
    [pscustomobject]@{ Path = 'CLAUDE.md'; Target = 'AGENTS.md'; Kind = 'File' }
    [pscustomobject]@{ Path = 'GROK.md'; Target = 'AGENTS.md'; Kind = 'File' }
)

$missing = @()
$wrongType = @()
$repaired = @()
$ok = @()

foreach ($spec in $specs) {
    $info = Get-LinkInfo -Path $spec.Path
    if (!$info.Exists) {
        $missing += $spec
        continue
    }
    if (!$info.IsLink) {
        $wrongType += $spec
        continue
    }
    if (!(Test-TargetEquals -Actual $info.Target -Expected $spec.Target)) {
        $missing += $spec
        continue
    }
    $ok += $spec.Path
}

Write-Host "Root: $repoRoot"
if ($ok.Count -gt 0) {
    Write-Host ("OK: " + ($ok -join ', '))
}

if ($wrongType.Count -gt 0) {
    foreach ($spec in $wrongType) {
        Write-Host "[block] $($spec.Path) exists but is not a symlink. Will not delete a regular $($spec.Kind)."
    }
}

if ($CheckOnly) {
    if ($missing.Count -eq 0 -and $wrongType.Count -eq 0) {
        Write-Host '[ok] Claude / Grok / Cursor links point at the canonical targets.'
        exit 0
    }
    Write-Host ("[missing] " + (($missing | ForEach-Object Path) -join ', '))
    exit 2
}

foreach ($spec in $missing) {
    $info = Get-LinkInfo -Path $spec.Path
    if ($info.Exists -and $info.IsLink) {
        if ($spec.Kind -eq 'Directory') {
            cmd /c "rmdir `"$($spec.Path)`"" | Out-Null
        }
        else {
            Remove-Item -LiteralPath $spec.Path -Force
        }
    }
    New-RelativeLink -LinkPath $spec.Path -Target $spec.Target -Kind $spec.Kind
    $repaired += "$($spec.Path) -> $($spec.Target)"
    Write-Host "[created] $($spec.Path) -> $($spec.Target)"
}

if ($wrongType.Count -gt 0) {
    Write-Host '[fail] Regular file/directory copies remain. Fix those paths manually.'
    exit 1
}

if ($repaired.Count -eq 0) {
    Write-Host '[ok] All agent links already exist. Nothing to do.'
    exit 0
}

Write-Host ''
Write-Host 'Agent links created or repaired. Do not git init or commit unless the user asks.'
exit 0
