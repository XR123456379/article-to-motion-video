param(
    [Parameter(Mandatory = $true)][string]$ProjectDir,
    [Parameter(Mandatory = $true)][string]$Storyboard
)

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$validator = Join-Path $skillRoot 'scripts\validate_storyboard.py'
$builder = Join-Path $skillRoot 'scripts\build_composition.py'
$resolvedProject = [System.IO.Path]::GetFullPath($ProjectDir)
$resolvedStoryboard = [System.IO.Path]::GetFullPath($Storyboard)
$outputHtml = Join-Path $resolvedProject 'index.html'

if (-not (Test-Path -LiteralPath $resolvedProject -PathType Container)) {
    throw "Project directory does not exist: $resolvedProject"
}
if (-not (Test-Path -LiteralPath $resolvedStoryboard -PathType Leaf)) {
    throw "Storyboard does not exist: $resolvedStoryboard"
}

python $validator $resolvedStoryboard
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python $builder $resolvedStoryboard $outputHtml
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $resolvedProject
try {
    npx.cmd hyperframes@0.8.31 lint
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}

Write-Host "Pipeline ready: $outputHtml"
Write-Host 'Next: run HyperFrames check --snapshots, inspect frames, then render the requested video.'
