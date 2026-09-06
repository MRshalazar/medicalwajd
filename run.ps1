<#
.SYNOPSISSaturday, September 5, 2026 at 11:52 PM
:heartpulse:
Click to react
:heart:
Click to react
:pink_heart:
Click to react
Add Reaction
More
September 6, 2026

    One-click startup script for the Privacy-Preserving CDSS system.
    Checks dependencies, starts all services, verifies them, and launches Doctor Console.
#>

$root = "D:\9raya\memoire 2026\Privacy-Preserving-CDSS"
$venvActivate = "$root\backend\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Privacy Preserving CDSS - System Startup" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 1. CHECK PROJECT
# ============================================================

if (-not (Test-Path $root)) {
    Write-Host "[ERROR] Project folder not found:" -ForegroundColor Red
    Write-Host "       $root" -ForegroundColor Yellow
    pause
    exit 1
}

# ============================================================
# 2. CHECK PYTHON VIRTUAL ENVIRONMENT
# ============================================================

if (-not (Test-Path $venvActivate)) {
    Write-Host "[ERROR] Python virtual environment not found:" -ForegroundColor Red
    Write-Host "        $venvActivate" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Create it with:" -ForegroundColor Yellow
    Write-Host "  cd '$root\backend'" -ForegroundColor White
    Write-Host "  python -m venv .venv" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r ..\requirements.txt" -ForegroundColor White
    pause
    exit 1
}

Write-Host "[OK] Project found" -ForegroundColor Green
Write-Host "[OK] Python virtual environment found" -ForegroundColor Green
Write-Host ""

# ============================================================
# 3. CHECK OLLAMA BEFORE STARTING ANYTHING
# ============================================================

Write-Host "Checking Ollama..." -ForegroundColor Cyan

$ollamaRunning = $false
$ollamaResponse = $null

try {
    $ollamaResponse = Invoke-RestMethod `
        -Uri "http://127.0.0.1:11434/api/tags" `
        -Method Get `
        -TimeoutSec 3

    $ollamaRunning = $true

    Write-Host "  [OK] Ollama is running on port 11434" -ForegroundColor Green
}
catch {
    Write-Host "  [!] Ollama is NOT running." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Ollama is required for the RAG system." -ForegroundColor Yellow
    Write-Host "  Starting Ollama automatically..." -ForegroundColor Cyan

    # Check whether ollama command exists
    $ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue

    if ($null -eq $ollamaCommand) {
        Write-Host ""
        Write-Host "[ERROR] Ollama command not found." -ForegroundColor Red
        Write-Host "Please install Ollama first." -ForegroundColor Yellow
        pause
        exit 1
    }

    # Start Ollama in a separate window
    Start-Process powershell -ArgumentList `
        "-NoExit",
        "-Command",
        "ollama serve"

    Write-Host "  Waiting for Ollama..." -ForegroundColor Yellow

    for ($i = 0; $i -lt 20; $i++) {

        Start-Sleep -Seconds 1

        try {
            $ollamaResponse = Invoke-RestMethod `
                -Uri "http://127.0.0.1:11434/api/tags" `
                -Method Get `
                -TimeoutSec 2

            $ollamaRunning = $true
            break
        }
        catch {
            # Keep waiting
        }
    }

    if ($ollamaRunning) {
        Write-Host "  [OK] Ollama started successfully" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "[ERROR] Ollama could not be started." -ForegroundColor Red
        Write-Host "Try manually running:" -ForegroundColor Yellow
        Write-Host "  ollama serve" -ForegroundColor White
        pause
        exit 1
    }
}

# ============================================================
# 4. CHECK REQUIRED OLLAMA MODELS
# ============================================================

Write-Host ""
Write-Host "Checking Ollama models..." -ForegroundColor Cyan

$models = @()

if ($null -ne $ollamaResponse.models) {
    $models = $ollamaResponse.models | ForEach-Object {
        $_.name
    }
}

$hasLlama = $models | Where-Object {
    $_ -like "llama3*"
}

$hasEmbedding = $models | Where-Object {
    $_ -like "nomic-embed-text*"
}

if ($hasLlama) {
    Write-Host "  [OK] llama3 found" -ForegroundColor Green
}
else {
    Write-Host "  [!] llama3 not found" -ForegroundColor Yellow
    Write-Host "      Run: ollama pull llama3" -ForegroundColor Yellow
}

if ($hasEmbedding) {
    Write-Host "  [OK] nomic-embed-text found" -ForegroundColor Green
}
else {
    Write-Host "  [ERROR] nomic-embed-text not found" -ForegroundColor Red
    Write-Host "          Run: ollama pull nomic-embed-text" -ForegroundColor Yellow

    Write-Host ""
    Write-Host "The RAG system cannot work without nomic-embed-text." -ForegroundColor Red
    pause
    exit 1
}

# ============================================================
# 5. CHECK ZKP ENGINE
# ============================================================

Write-Host ""
Write-Host "Checking ZKP Engine..." -ForegroundColor Cyan

$zkpEngine = "$root\zkp_engine\target\release\zkp_engine.exe"

if (Test-Path $zkpEngine) {
    Write-Host "  [OK] Bulletproof ZKP engine found" -ForegroundColor Green
}
else {
    Write-Host "  [WARNING] ZKP engine not found:" -ForegroundColor Yellow
    Write-Host "            $zkpEngine" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Build it with:" -ForegroundColor Yellow
    Write-Host "  cd '$root\zkp_engine'" -ForegroundColor White
    Write-Host "  cargo build --release" -ForegroundColor White
}

# ============================================================
# 6. CHECK CHROMADB
# ============================================================

Write-Host ""
Write-Host "Checking ChromaDB..." -ForegroundColor Cyan

$chromaDb = "$root\knowledge_mcp\chroma_db"

if (Test-Path $chromaDb) {
    Write-Host "  [OK] ChromaDB found" -ForegroundColor Green
}
else {
    Write-Host "  [WARNING] ChromaDB directory not found:" -ForegroundColor Yellow
    Write-Host "            $chromaDb" -ForegroundColor Yellow
}

# ============================================================
# FUNCTION: CHECK TCP PORT
# ============================================================

function Test-Port {
    param(
        [int]$Port
    )

    try {
        $connection = Test-NetConnection `
            -ComputerName "127.0.0.1" `
            -Port $Port `
            -WarningAction SilentlyContinue

        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

# ============================================================
# FUNCTION: WAIT FOR PORT
# ============================================================

function Wait-ForPort {
    param(
        [int]$Port,
        [string]$ServiceName,
        [int]$MaxAttempts = 30
    )

    Write-Host "  Waiting for $ServiceName on port $Port..." -ForegroundColor Yellow

    for ($i = 0; $i -lt $MaxAttempts; $i++) {

        if (Test-Port -Port $Port) {
            Write-Host "  [OK] $ServiceName is running on port $Port" -ForegroundColor Green
            return $true
        }

        Start-Sleep -Seconds 1
    }

    Write-Host "  [ERROR] $ServiceName failed to start on port $Port" -ForegroundColor Red
    return $false
}

# ============================================================
# 7. START SERVICES
# ============================================================

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Starting CDSS Services" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# Patient MCP :8005
# ------------------------------------------------------------

Write-Host "[1/6] Starting Patient MCP :8005" -ForegroundColor Cyan

Start-Process powershell -ArgumentList `
    "-NoExit",
    "-Command",
    "cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn patient_mcp.app:app --reload --port 8005"

# ------------------------------------------------------------
# Rule Engine :8004
# ------------------------------------------------------------

Write-Host "[2/6] Starting Rule Engine :8004" -ForegroundColor Cyan

Start-Process powershell -ArgumentList `
    "-NoExit",
    "-Command",
    "cd '$root'; .\backend\.venv\Scripts\Activate.ps1; `$env:OLLAMA_HOST='http://127.0.0.1:11434'; uvicorn rule_engine.app:app --reload --port 8004"

# ------------------------------------------------------------
# Privacy MCP :8003
# ------------------------------------------------------------

Write-Host "[3/6] Starting Privacy MCP :8003" -ForegroundColor Cyan

Start-Process powershell -ArgumentList `
    "-NoExit",
    "-Command",
    "cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn privacy_mcp.app:app --reload --port 8003"

# ------------------------------------------------------------
# Decision Engine :8002
# ------------------------------------------------------------

Write-Host "[4/6] Starting Decision Engine :8002" -ForegroundColor Cyan

Start-Process powershell -ArgumentList `
    "-NoExit",
    "-Command",
    "cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn decision_engine.app:app --reload --port 8002"

# ------------------------------------------------------------
# Knowledge MCP :8010
# ------------------------------------------------------------

Write-Host "[5/6] Starting Knowledge MCP :8010" -ForegroundColor Cyan

Start-Process powershell -ArgumentList `
    "-NoExit",
    "-Command",
    "cd '$root'; .\backend\.venv\Scripts\Activate.ps1; `$env:OLLAMA_HOST='http://127.0.0.1:11434'; uvicorn knowledge_mcp.app:app --reload --port 8010"

# ------------------------------------------------------------
# LangGraph Coordinator :8007
# ------------------------------------------------------------

Write-Host "[6/6] Starting LangGraph Coordinator :8007" -ForegroundColor Cyan

Start-Process powershell -ArgumentList `
    "-NoExit",
    "-Command",
    "cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn langgraph_coordinator.app:app --reload --port 8007"

# ============================================================
# 8. WAIT FOR SERVICES
# ============================================================

Write-Host ""
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Write-Host ""

$services = @(
    @{Port = 8005; Name = "Patient MCP"},
    @{Port = 8004; Name = "Rule Engine"},
    @{Port = 8003; Name = "Privacy MCP"},
    @{Port = 8002; Name = "Decision Engine"},
    @{Port = 8010; Name = "Knowledge MCP"},
    @{Port = 8007; Name = "LangGraph Coordinator"}
)

$allReady = $true

foreach ($service in $services) {

    $ready = Wait-ForPort `
        -Port $service.Port `
        -ServiceName $service.Name

    if (-not $ready) {
        $allReady = $false
    }
}

# ============================================================
# 9. FINAL STATUS
# ============================================================

Write-Host ""

if (-not $allReady) {

    Write-Host "====================================================" -ForegroundColor Red
    Write-Host "  XXXXXXX SYSTEM STARTUP FAILED" -ForegroundColor Red
    Write-Host "====================================================" -ForegroundColor Red
    Write-Host ""

    Write-Host "Check the individual PowerShell service windows." -ForegroundColor Yellow
    Write-Host ""

    pause
    exit 1
}

Write-Host "====================================================" -ForegroundColor Green
Write-Host "  -/ ALL CDSS SERVICES ARE RUNNING" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""

Write-Host "System status:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ollama                 :11434   -/" -ForegroundColor Green
Write-Host "  Patient MCP            :8005    -/" -ForegroundColor Green
Write-Host "  Rule Engine            :8004    -/" -ForegroundColor Green
Write-Host "  Privacy MCP            :8003    -/" -ForegroundColor Green
Write-Host "  Decision Engine        :8002    -/" -ForegroundColor Green
Write-Host "  Knowledge MCP / RAG    :8010    -/" -ForegroundColor Green
Write-Host "  LangGraph Coordinator  :8007    -/" -ForegroundColor Green
Write-Host ""

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Starting Doctor Console" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 2

# ============================================================
# 10. LAUNCH DOCTOR CONSOLE
# ============================================================

Set-Location $root

& "$root\backend\.venv\Scripts\python.exe" "$root\doctor_console.py"

Write-Host ""
Write-Host "Doctor Console closed." -ForegroundColor Yellow
pause