#!/usr/bin/env bash
# ==============================================================================
# DevPilot SRE Platform - Script Oficial de Verificación de la Etapa de Build (Bash)
# Uso: chmod +x verify-build.sh && ./verify-build.sh
# ==============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${CYAN}===========================================================================${NC}"
echo -e "${CYAN}  🚀 DEVPILOT SRE ENGINE - VALIDACIÓN DE LA ETAPA DE BUILD (CI/CD)          ${NC}"
echo -e "${CYAN}===========================================================================${NC}"

echo -e "\n${YELLOW}1. ANÁLISIS ESTÁTICO Y COMPILACIÓN SINTÁCTICA (PYTHON & NODE.JS)${NC}"
python3 -m py_compile devpilot_core/main.py devpilot_core/database.py devpilot_core/auth.py \
    devpilot_core/monitor.py devpilot_core/docker_manager.py devpilot_core/ai_agent.py \
    microservices/products/main.py microservices/orders/main.py microservices/payments/main.py
echo -e "  [${GREEN}✓ PASS${NC}] Python AST: Todos los archivos Python compilaron sin errores"

node --check microservices/users/server.js
echo -e "  [${GREEN}✓ PASS${NC}] Node.js AST: microservices/users/server.js sintaxis válida"

for js in devpilot_core/static/models/*.js devpilot_core/static/controllers/*.js devpilot_core/static/views/*.js devpilot_core/static/js/*.js; do
    node --check "$js"
done
echo -e "  [${GREEN}✓ PASS${NC}] Frontend MVVM: 14 módulos JavaScript validados"

echo -e "\n${YELLOW}2. AUDITORÍA DE DEPENDENCIAS Y CONTEXTO DOCKER${NC}"
test -f .dockerignore && test -f devpilot_core/.dockerignore && test -f microservices/users/.dockerignore
echo -e "  [${GREEN}✓ PASS${NC}] Archivos .dockerignore presentes y activos"

echo -e "\n${YELLOW}3. PRUEBAS AUTOMATIZADAS UNITARIAS Y DE CONTRATO${NC}"
pytest tests/ -v
echo -e "  [${GREEN}✓ PASS${NC}] Suite Pytest: Pruebas unitarias y contratos superados"

(cd microservices/users && npm test)
echo -e "  [${GREEN}✓ PASS${NC}] Users Service: Pruebas unitarias de Node.js superadas"

echo -e "\n${YELLOW}4. VALIDACIÓN DE DOCKER COMPOSE${NC}"
docker compose config > /dev/null
echo -e "  [${GREEN}✓ PASS${NC}] docker-compose.yml: Topología de servicios validada con 0 errores"

echo -e "\n${GREEN}***************************************************************************${NC}"
echo -e "${GREEN}  ESTADO: ✅ BUILD EXITOSO (Quality Gate Aprobado)                         ${NC}"
echo -e "${GREEN}***************************************************************************${NC}\n"
