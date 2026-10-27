Write-Host "==========================================" -ForegroundColor Red
Write-Host " SentinelMesh — Reset Live Demo Database " -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Red
Write-Host "This will permanently truncate all live records from:" -ForegroundColor Yellow
Write-Host " - messages" -ForegroundColor Yellow
Write-Host " - trust_edges" -ForegroundColor Yellow
Write-Host " - agents" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Type 'RESET' to confirm truncation of live database"

if ($confirmation -eq "RESET") {
    Write-Host "Truncating tables in live database..." -ForegroundColor Cyan
    docker exec sentinelmesh-postgres-1 psql -U sentinel -d sentinelmesh -c "TRUNCATE messages, trust_edges, agents CASCADE;"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Live database reset complete. All agents, messages, and trust edges cleared." -ForegroundColor Green
    } else {
        Write-Host "Failed to truncate tables. Check if postgres container is running." -ForegroundColor Red
    }
} else {
    Write-Host "Reset aborted. No changes were made." -ForegroundColor Gray
}
