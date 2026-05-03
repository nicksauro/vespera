$ErrorActionPreference = 'Stop'
$src = 'D:\Algotrader\dll-backfill'
$qdir = 'D:\Algotrader\dll-backfill-quarantine-2026-05-03'
New-Item -ItemType Directory -Path $qdir -Force | Out-Null

$contaminated = @(
  'test-chunk3-isolated',
  'test-multi',
  'test-multi-v2',
  'test-orchestrator',
  'test-orchestrator-v2',
  'smoke-test',
  'verify-2023-12-29'
)

$moved = 0
$missing = 0
foreach ($d in $contaminated) {
    $from = Join-Path $src $d
    $to   = Join-Path $qdir $d
    if (Test-Path $from) {
        Move-Item -Path $from -Destination $to -Force
        Write-Host ("Moved: {0,-25} -> quarantine" -f $d)
        $moved++
    } else {
        Write-Host ("Not found (skip): {0}" -f $d)
        $missing++
    }
}

Write-Host ""
Write-Host ("Summary: moved={0} missing={1}" -f $moved, $missing)
Write-Host ""
Write-Host "=== Verify src has only WDOFUT_* + scaffolding ==="
$leftover = Get-ChildItem $src | Where-Object { $_.PSIsContainer -and $_.Name -notlike 'WDOFUT_*' }
if ($leftover) {
    Write-Host "LEFTOVER non-WDOFUT dirs in src:" -ForegroundColor Red
    $leftover | Format-Table Name
} else {
    Write-Host "Clean: only WDOFUT_* dirs remain in src" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Quarantine target inventory ==="
Get-ChildItem $qdir | Format-Table Name, LastWriteTime

Write-Host ""
Write-Host "=== Manifest sanity check ==="
$manifestPath = Join-Path $src 'manifest.csv'
if (Test-Path $manifestPath) {
    $lines = (Get-Content $manifestPath | Measure-Object -Line).Lines
    Write-Host ("manifest.csv line count: {0}" -f $lines)
    Write-Host "First 3 lines:"
    Get-Content $manifestPath | Select-Object -First 3
} else {
    Write-Host "manifest.csv NOT FOUND" -ForegroundColor Red
}
