<#
.SYNOPSIS
    Clean the XYZShop project: remove Python bytecode caches and other
    generated artifacts to start from a fresh state.

.DESCRIPTION
    Deletes all __pycache__ directories and compiled Python files (*.pyc, *.pyo)
    from the project, plus optional tool caches. The virtual environment (.venv)
    is skipped by default so you don't have to reinstall dependencies.

.PARAMETER IncludeVenv
    Also clean caches inside the .venv folder.

.PARAMETER All
    Additionally remove .pytest_cache, .mypy_cache, and the collected
    staticfiles/ directory.

.EXAMPLE
    .\clean.ps1
    Remove __pycache__ and *.pyc/*.pyo from the project (excluding .venv).

.EXAMPLE
    .\clean.ps1 -All
    Also remove test/type caches and the staticfiles/ directory.

.NOTES
    Usage summary:
      .\clean.ps1                # remove all __pycache__ dirs + *.pyc/*.pyo (skips .venv)
      .\clean.ps1 -All           # also remove .pytest_cache, .mypy_cache, staticfiles/
      .\clean.ps1 -IncludeVenv   # also clean caches inside .venv
#>

[CmdletBinding()]
param(
    [switch]$IncludeVenv,
    [switch]$All
)

$ErrorActionPreference = 'Stop'

# Work from the directory this script lives in (the project root).
$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
Push-Location $root

Write-Host "Cleaning project at: $root" -ForegroundColor Cyan

function Remove-Items {
    param(
        [Parameter(Mandatory)] [string] $Label,
        [AllowNull()] [AllowEmptyCollection()] [System.Object[]] $Items
    )
    $count = ($Items | Measure-Object).Count
    if ($count -eq 0) {
        Write-Host "  - $Label`: nothing to remove" -ForegroundColor DarkGray
        return
    }
    $Items | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  - $Label`: removed $count item(s)" -ForegroundColor Green
}

# Build an exclusion filter for the .venv folder unless -IncludeVenv is set.
$venvPath = Join-Path $root '.venv'
function Test-Excluded {
    param([string]$Path)
    if ($IncludeVenv) { return $false }
    return $Path.StartsWith($venvPath, [System.StringComparison]::OrdinalIgnoreCase)
}

# 1. __pycache__ directories
$pycache = Get-ChildItem -Path $root -Recurse -Force -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue |
    Where-Object { -not (Test-Excluded $_.FullName) }
Remove-Items -Label '__pycache__ directories' -Items $pycache

# 2. Compiled Python files
$pyc = Get-ChildItem -Path $root -Recurse -Force -File -Include '*.pyc', '*.pyo' -ErrorAction SilentlyContinue |
    Where-Object { -not (Test-Excluded $_.FullName) }
Remove-Items -Label 'compiled Python files (*.pyc/*.pyo)' -Items $pyc

# 3. Optional extra caches
if ($All) {
    $extra = @()
    foreach ($name in '.pytest_cache', '.mypy_cache', 'staticfiles') {
        $path = Join-Path $root $name
        if (Test-Path $path) { $extra += Get-Item $path }
    }
    Remove-Items -Label 'tool caches (.pytest_cache/.mypy_cache/staticfiles)' -Items $extra
}

Write-Host "Done. Project is clean." -ForegroundColor Cyan
Pop-Location
