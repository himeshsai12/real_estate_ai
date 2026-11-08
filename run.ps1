Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ESTATESPHERE REAL ESTATE PLATFORM WITH PROPERTY AGENTS    " -ForegroundColor Gold
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting EstateSphere server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""
python server.py 8000
