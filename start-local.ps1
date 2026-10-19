# ==============================================================================
# DevPilot SRE Platform - Script de Arranque Nativo (Modo Software Standalone)
# Propósito: Levanta todos los microservicios y DevPilot Core directamente sobre
#            Windows SIN Docker, para pruebas locales y exposiciones.
# Uso: .\start-local.ps1
# ==============================================================================

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "  🚀 INICIANDO DEVPILOT EN MODO SOFTWARE NATIVO (SIN DOCKER)              " -ForegroundColor Cyan
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = $PSScriptRoot

# Función para verificar si un puerto ya está ocupado
function Test-PortOccupied {
    param([int]$port)
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    return ($null -ne $conn)
}

# 1. Microservicio Users (Node.js :3001)
Write-Host "[1/5] Levantando Users Service (Node.js Express :3001)..." -ForegroundColor Yellow
if (-not (Test-PortOccupied 3001)) {
    Start-Process -FilePath "node" -ArgumentList "server.js" -WorkingDirectory "$baseDir\microservices\users" -WindowStyle Minimized
    Start-Sleep -Milliseconds 600
} else {
    Write-Host "      Puerto 3001 ya activo." -ForegroundColor DarkGray
}

# 2. Microservicio Products (Python FastAPI :3002)
Write-Host "[2/5] Levantando Products Service (FastAPI :3002)..." -ForegroundColor Yellow
if (-not (Test-PortOccupied 3002)) {
    Start-Process -FilePath "py" -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 3002" -WorkingDirectory "$baseDir\microservices\products" -WindowStyle Minimized
    Start-Sleep -Milliseconds 600
} else {
    Write-Host "      Puerto 3002 ya activo." -ForegroundColor DarkGray
}

# 3. Microservicio Orders (Python FastAPI :3003)
Write-Host "[3/5] Levantando Orders Service (FastAPI :3003)..." -ForegroundColor Yellow
if (-not (Test-PortOccupied 3003)) {
    Start-Process -FilePath "py" -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 3003" -WorkingDirectory "$baseDir\microservices\orders" -WindowStyle Minimized
    Start-Sleep -Milliseconds 600
} else {
    Write-Host "      Puerto 3003 ya activo." -ForegroundColor DarkGray
}

# 4. Microservicio Payments (Python FastAPI :3004)
Write-Host "[4/5] Levantando Payments Service (FastAPI :3004)..." -ForegroundColor Yellow
if (-not (Test-PortOccupied 3004)) {
    Start-Process -FilePath "py" -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 3004" -WorkingDirectory "$baseDir\microservices\payments" -WindowStyle Minimized
    Start-Sleep -Milliseconds 600
} else {
    Write-Host "      Puerto 3004 ya activo." -ForegroundColor DarkGray
}

# 5. DevPilot Core (Python FastAPI + Monitor + UI :8000)
Write-Host "[5/5] Levantando DevPilot Core (FastAPI :8000)..." -ForegroundColor Yellow
if (-not (Test-PortOccupied 8000)) {
    Start-Process -FilePath "py" -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000" -WorkingDirectory "$baseDir\devpilot_core" -WindowStyle Minimized
    Start-Sleep -Seconds 2
} else {
    Write-Host "      Puerto 8000 ya activo." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "***************************************************************************" -ForegroundColor Green
Write-Host "  ✅ TODOS LOS SERVICIOS ESTÁN EJECUTÁNDOSE EN MODO SOFTWARE PURO" -ForegroundColor Green
Write-Host "***************************************************************************" -ForegroundColor Green
Write-Host "  - DevPilot Dashboard SPA : http://localhost:8000" -ForegroundColor White
Write-Host "  - Users Service API      : http://localhost:3001/health" -ForegroundColor Gray
Write-Host "  - Products Service API   : http://localhost:3002/health" -ForegroundColor Gray
Write-Host "  - Orders Service API     : http://localhost:3003/health" -ForegroundColor Gray
Write-Host "  - Payments Service API   : http://localhost:3004/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Para detener todos los servicios usa: .\stop-local.ps1" -ForegroundColor Cyan
Write-Host ""
