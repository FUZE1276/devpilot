#!/usr/bin/env bash
# ==============================================================================
# DevPilot SRE Platform - Script de Detención Linux/macOS
# Uso: chmod +x stop-local.sh && ./stop-local.sh
# ==============================================================================

echo ">> Deteniendo procesos en puertos 8000, 3001, 3002, 3003, 3004..."
fuser -k 8000/tcp 3001/tcp 3002/tcp 3003/tcp 3004/tcp 2>/dev/null || true
echo ">> Procesos locales detenidos."
