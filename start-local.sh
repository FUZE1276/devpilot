#!/usr/bin/env bash
# ==============================================================================
# DevPilot SRE Platform - Script de Arranque Nativo Linux/macOS
# Uso: chmod +x start-local.sh && ./start-local.sh
# ==============================================================================

echo ">> Levantando DevPilot en modo software nativo..."

(cd microservices/users && node server.js) > /dev/null 2>&1 &
(cd microservices/products && python3 -m uvicorn main:app --host 127.0.0.1 --port 3002) > /dev/null 2>&1 &
(cd microservices/orders && python3 -m uvicorn main:app --host 127.0.0.1 --port 3003) > /dev/null 2>&1 &
(cd microservices/payments && python3 -m uvicorn main:app --host 127.0.0.1 --port 3004) > /dev/null 2>&1 &
(cd devpilot_core && python3 -m uvicorn main:app --host 127.0.0.1 --port 8000) > /dev/null 2>&1 &

echo ">> Todos los servicios levantados en segundo plano."
echo ">> Dashboard: http://localhost:8000"
