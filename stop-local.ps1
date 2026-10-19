# ==============================================================================
# DevPilot SRE Platform - Script de Detención de Procesos Locales
# Propósito: Detiene limpiamente los procesos en puertos 8000, 3001, 3002, 3003, 3004.
# Uso: .\stop-local.ps1
# ==============================================================================

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Yellow
Write-Host "  🛑 DETENIENDO TODOS LOS SERVICIOS LOCALES DE DEVPILOT                  " -ForegroundColor Yellow
Write-Host "===========================================================================" -ForegroundColor Yellow
Write-Host ""

$ports = @(8000, 3001, 3002, 3003, 3004)

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    if ($connections) {
        $pidsToKill = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pidToKill in $pidsToKill) {
            try {
                $proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "  [DETENIENDO] Puerto $port -> Proceso $($proc.ProcessName) (PID: $pidToKill)" -ForegroundColor Red
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                }
            } catch {
                Write-Host "  [WARN] No se pudo detener PID $pidToKill: $_" -ForegroundColor DarkGray
            }
        }
    } else {
        Write-Host "  [INACTIVO] Puerto $port libre." -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "  ✓ Todos los procesos locales de DevPilot han sido detenidos." -ForegroundColor Green
Write-Host ""
