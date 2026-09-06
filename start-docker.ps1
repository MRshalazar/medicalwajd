$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not available in PATH."
    exit 1
}

Write-Host "Starting Privacy-Preserving CDSS containers..." -ForegroundColor Cyan

docker compose up --build -d

docker compose ps

Write-Host "" 
Write-Host "Use the following commands to inspect logs:" -ForegroundColor Yellow
Write-Host "  docker compose logs -f" -ForegroundColor Gray
Write-Host "  docker compose down" -ForegroundColor Gray
