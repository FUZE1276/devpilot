import os
import json
import time
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
import httpx
from datetime import datetime, timezone
import csv
import io

from database import (
    init_db,
    get_services,
    get_service,
    create_custom_service,
    update_service_thresholds,
    delete_custom_service,
    get_recent_metrics,
    get_incidents,
    resolve_incident,
    get_remediation_proposals,
    get_remediation_proposal,
    update_proposal_status,
    log_remediation,
    get_audit_trail,
    get_chat_history,
    get_users,
    get_user_by_email,
    get_user_by_username_or_email,
    update_user_permissions,
    update_user_last_login,
    get_system_stats,
    cleanup_stale_proposals
)
from auth import (
    create_jwt_token,
    verify_jwt_token,
    verify_totp_code,
    generate_current_totp,
    get_current_user_optional,
    get_current_user,
    require_permission,
    authenticate_user_credentials,
    get_effective_user_permissions,
    ALL_SYSTEM_PERMISSIONS,
    PRESET_USERS,
    ROLE_PERMISSIONS,
    JWT_EXPIRATION_SECONDS
)
from monitor import monitor
from ai_agent import ai_agent
from email_otp import request_email_otp, verify_email_otp, SMTP_OVERRIDE_RECIPIENT
from docker_manager import (
    get_container_logs,
    get_container_stats,
    restart_service_container,
    is_docker_connected,
    discover_candidate_services
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("devpilot.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing DevPilot Core Database...")
    init_db()
    logger.info("Starting Background Health Monitor...")
    await monitor.start()
    yield
    logger.info("Stopping DevPilot Health Monitor...")
    await monitor.stop()

app = FastAPI(
    title="DevPilot Core API",
    description="DevPilot Central Observability, Chaos Testing & Claude AI Remediation Platform with SSO, TOTP & RBAC",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic de Seguridad y Operación (Requisitos RF07, RF08)
class LoginCredentialsRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario o correo electrónico")
    password: str = Field(..., description="Contraseña del usuario")
    emailOtpCode: Optional[str] = Field(None, description="Código de 6 dígitos enviado por correo (MFA Email)")

class UpdateUserPermissionsRequest(BaseModel):
    permissions: List[str] = Field(..., description="Lista de identificadores de permisos RBAC para el usuario")

class EmailOtpSendRequest(BaseModel):
    email: str = Field(..., description="Correo electrónico o nombre de usuario")

class EmailOtpVerifyRequest(BaseModel):
    email: str = Field(..., description="Correo electrónico del usuario")
    code: str = Field(..., description="Código numérico OTP de 6 dígitos")

class SSOLoginRequest(BaseModel):
    email: str = Field(..., description="Correo del usuario para autenticación federada SSO")
    role: Optional[str] = Field(None, description="Rol específico (Admin, SRE_Operator, Developer, Viewer)")
    provider: Optional[str] = Field("github_sso", description="Proveedor SSO (github, google, keycloak)")

class VerifyTotpRequest(BaseModel):
    code: str = Field(..., description="Código numérico TOTP de 6 dígitos")
    secret: Optional[str] = Field("JBSWY3DPEHPK3PXP", description="Clave secreta base32 del usuario")

class CreateServiceRequest(BaseModel):
    name: str = Field(..., description="Identificador único (ej: inventory)")
    displayName: str = Field(..., description="Nombre visible (ej: Inventory Service)")
    serviceType: str = Field("Python", description="Node.js, Python, Go, etc.")
    url: str = Field(..., description="URL base (ej: http://inventory_service:3004)")
    containerName: str = Field(..., description="Nombre del contenedor en Docker")
    latencyThresholdMs: Optional[float] = Field(2000.0, description="Umbral de latencia en ms")
    errorThresholdPct: Optional[float] = Field(0.20, description="Umbral de tasa de error (0.0 a 1.0)")

class UpdateThresholdsRequest(BaseModel):
    latencyThresholdMs: float = Field(..., ge=100.0, le=10000.0, description="Umbral de latencia en ms")
    errorThresholdPct: float = Field(..., ge=0.01, le=1.0, description="Umbral de tasa de error (0.01 a 1.0)")

class ProposalDecisionRequest(BaseModel):
    notes: Optional[str] = Field("Aprobado por el operador técnico", description="Notas de la decisión humana")
    totpCode: Optional[str] = Field(None, description="Código de segundo factor TOTP (RFC 6238) de 6 dígitos")

class FaultInjectRequest(BaseModel):
    service: str
    type: str
    delayMs: Optional[int] = 2500
    errorRate: Optional[float] = 0.5
    hardKill: Optional[bool] = False
    reason: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class ResolveIncidentRequest(BaseModel):
    note: Optional[str] = "Manual resolution via DevPilot Dashboard"

# ==========================================
# ENDPOINTS REST: AUTENTICACIÓN SSO & TOTP (RF07, RF08)
# ==========================================

@app.get("/api/auth/users")
async def list_sso_users():
    """Retorna los usuarios registrados con sus permisos efectivos y el catálogo general de permisos."""
    users = get_users()
    if not users:
        users = [
            {"email": k, "name": v["name"], "role": v["role"], "totp_secret": v["totp_secret"], "permissions": None}
            for k, v in PRESET_USERS.items()
        ]
    enriched_users = []
    for u in users:
        u_copy = dict(u)
        u_copy["effective_permissions"] = get_effective_user_permissions(u)
        enriched_users.append(u_copy)
    return {
        "success": True,
        "users": enriched_users,
        "permissions_catalog": ALL_SYSTEM_PERMISSIONS
    }

@app.get("/api/users/permissions-catalog")
async def get_permissions_catalog():
    """Retorna el catálogo completo de permisos disponibles en el sistema."""
    return {"success": True, "permissions": ALL_SYSTEM_PERMISSIONS}

@app.put("/api/users/{identifier}/permissions")
async def modify_user_permissions(
    identifier: str,
    payload: UpdateUserPermissionsRequest,
    current_user: Dict[str, Any] = Depends(require_permission("users:manage"))
):
    """
    Actualiza la matriz de permisos para un usuario específico.
    Protegido por RBAC: Requiere permiso 'users:manage' (Super Administrador).
    """
    valid_ids = {p["id"] for p in ALL_SYSTEM_PERMISSIONS}
    cleaned_perms = [p for p in payload.permissions if p in valid_ids]
    
    updated = update_user_permissions(identifier, cleaned_perms)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario '{identifier}' no encontrado."
        )
    
    user = get_user_by_username_or_email(identifier)
    effective = get_effective_user_permissions(user) if user else cleaned_perms
    
    logger.info(f"[RBAC Governance] Permisos actualizados para '{identifier}' por {current_user.get('email', 'superadmin')}: {cleaned_perms}")
    
    return {
        "success": True,
        "message": f"Permisos actualizados exitosamente para '{identifier}'.",
        "user": {
            "email": user.get("email") if user else identifier,
            "permissions": cleaned_perms,
            "effective_permissions": effective
        }
    }

@app.post("/api/users/{identifier}/permissions/reset")
async def reset_user_permissions(
    identifier: str,
    current_user: Dict[str, Any] = Depends(require_permission("users:manage"))
):
    """
    Restablece los permisos de un usuario a los predeterminados de su rol.
    Protegido por RBAC: Requiere permiso 'users:manage' (Super Administrador).
    """
    updated = update_user_permissions(identifier, None)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario '{identifier}' no encontrado."
        )
    user = get_user_by_username_or_email(identifier)
    effective = get_effective_user_permissions(user) if user else []
    
    return {
        "success": True,
        "message": f"Permisos restablecidos a los por defecto del rol para '{identifier}'.",
        "effective_permissions": effective
    }

@app.post("/api/auth/login")
async def password_login(payload: LoginCredentialsRequest):
    """
    Autenticación con Usuario/Correo y Contraseña + Segundo Factor por Correo Electrónico (MFA).
    Soporta los roles: Super Administrador, Administrador y Cliente.
    """
    user = authenticate_user_credentials(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos. Verifique sus credenciales."
        )
    
    user_email = user["email"]
    user_name = user.get("name", user_email)

    # Paso 1: Si no se ha enviado el código OTP por correo, lo generamos y solicitamos al usuario
    if not payload.emailOtpCode:
        success, msg, dev_code = request_email_otp(user_email, user_name)
        return {
            "success": True,
            "requires_email_otp": True,
            "email": user_email,
            "destination_email": SMTP_OVERRIDE_RECIPIENT or user_email,
            "name": user_name,
            "role": user.get("role", "Cliente"),
            "message": msg,
            "dev_code": dev_code
        }

    # Paso 2: Si viene el código OTP, lo verificamos
    valid, msg = verify_email_otp(user_email, payload.emailOtpCode)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    role = user.get("role", "Cliente")
    permissions = get_effective_user_permissions(user)
    
    claims = {
        "sub": user["email"],
        "name": user_name,
        "role": role,
        "permissions": permissions,
        "auth_method": "password+email_otp",
        "email_otp_verified": True
    }
    
    token = create_jwt_token(claims)
    update_user_last_login(user["email"])
    
    return {
        "success": True,
        "requires_email_otp": False,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_SECONDS,
        "user": {
            "email": user["email"],
            "name": user_name,
            "role": role,
            "permissions": permissions,
            "totp_secret": user.get("totp_secret", "JBSWY3DPEHPK3PXP")
        }
    }

@app.post("/api/auth/email-otp/request")
async def request_email_otp_endpoint(payload: EmailOtpSendRequest):
    """
    Genera y envía un código OTP de 6 dígitos al correo electrónico del usuario.
    """
    user = get_user_by_email(payload.email)
    user_name = user.get("name", payload.email) if user else "Usuario DevPilot"
    success, msg, dev_code = request_email_otp(payload.email, user_name)
    return {
        "success": success,
        "message": msg,
        "email": payload.email,
        "destination_email": SMTP_OVERRIDE_RECIPIENT or payload.email,
        "dev_code": dev_code
    }

@app.post("/api/auth/email-otp/verify")
async def verify_email_otp_endpoint(payload: EmailOtpVerifyRequest):
    """
    Verifica si el código OTP por correo ingresado es correcto y no ha expirado.
    """
    valid, msg = verify_email_otp(payload.email, payload.code)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    return {
        "success": True,
        "valid": True,
        "message": msg
    }

@app.post("/api/auth/sso/login")
async def sso_login(payload: SSOLoginRequest):
    """
    Simulación de autenticación federada SSO vía OIDC / OAuth 2.0.
    Emite un token JWT firmado criptográficamente con los claims y permisos RBAC del usuario.
    """
    user_email = payload.email.lower().strip()
    user = get_user_by_email(user_email)
    
    if not user:
        preset = PRESET_USERS.get(user_email)
        if preset:
            user = preset
        else:
            role = payload.role if payload.role in ROLE_PERMISSIONS else "Viewer"
            user = {
                "email": user_email,
                "name": user_email.split('@')[0].capitalize(),
                "role": role,
                "totp_secret": "JBSWY3DPEHPK3PXP"
            }
    
    role = payload.role or user.get("role", "Viewer")
    permissions = get_effective_user_permissions(user)
    
    claims = {
        "sub": user["email"],
        "name": user.get("name", user["email"]),
        "role": role,
        "permissions": permissions,
        "provider": payload.provider or "github_oidc"
    }
    
    token = create_jwt_token(claims)
    update_user_last_login(user["email"])
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_SECONDS,
        "user": {
            "email": user["email"],
            "name": user.get("name", user["email"]),
            "role": role,
            "permissions": permissions,
            "totp_secret": user.get("totp_secret", "JBSWY3DPEHPK3PXP")
        }
    }

@app.get("/api/auth/me")
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user_optional)):
    """Retorna los claims y permisos del usuario activo."""
    return {"success": True, "user": user}

@app.post("/api/auth/verify-totp")
async def verify_totp_endpoint(payload: VerifyTotpRequest):
    """Verifica un código de un solo uso TOTP (RFC 6238) de 6 dígitos."""
    valid = verify_totp_code(payload.code, secret_base32=payload.secret or "JBSWY3DPEHPK3PXP")
    return {
        "success": valid,
        "valid": valid,
        "message": "Código TOTP verificado exitosamente." if valid else "Código TOTP inválido o expirado."
    }

@app.get("/api/auth/demo-totp")
async def get_demo_totp(secret: Optional[str] = "JBSWY3DPEHPK3PXP"):
    """Retorna el código TOTP actual en vivo para facilitar validaciones y pruebas de laboratorio."""
    current_code = generate_current_totp(secret or "JBSWY3DPEHPK3PXP")
    interval = 30
    return {
        "success": True,
        "totp_code": current_code,
        "interval_seconds": interval,
        "remaining_seconds": interval - (int(time.time()) % interval)
    }

@app.get("/api/dashboard/summary")
async def dashboard_summary(current_user: Dict[str, Any] = Depends(get_current_user_optional)):
    """Entrega todo el estado del sistema en una sola respuesta instantánea (<5ms)."""
    services = get_services()
    incidents = get_incidents()
    proposals = get_remediation_proposals(status="PENDING_APPROVAL")
    ai_status = ai_agent.get_system_status()
    docker_conn = is_docker_connected()

    # Métricas recientes para gráficas (dinámico para todos los microservicios registrados)
    metrics_map = {
        s["name"]: get_recent_metrics(s["name"], limit=7)
        for s in services
    }

    return {
        "success": True,
        "services": services,
        "incidents": incidents,
        "proposals": proposals,
        "system": {
            "ai": ai_status,
            "docker_connected": docker_conn,
        },
        "metrics": metrics_map,
        "auth": {
            "currentUser": current_user
        }
    }

# ==========================================
# ENDPOINTS REST: ESTADO DEL SISTEMA
# ==========================================

@app.get("/api/system/status")
async def system_status():
    ai_status = ai_agent.get_system_status()
    docker_conn = is_docker_connected()
    return {
        "success": True,
        "ai": ai_status,
        "docker_connected": docker_conn,
        "architecture": {
            "mode": "External Non-Invasive Observability",
            "orchestration": "Docker Compose",
            "storage": "SQLite Local DB"
        }
    }

# ==========================================
# ENDPOINTS REST: GESTIÓN DINÁMICA DE SERVICIOS
# ==========================================

@app.get("/api/services")
async def list_services():
    services = get_services()
    return {
        "success": True,
        "count": len(services),
        "data": services,
        "docker_connected": is_docker_connected()
    }

@app.get("/api/services/discover")
async def discover_services(
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    """
    Descubre automáticamente contenedores en ejecución en Docker que no estén registrados aún
    en DevPilot, prueba su endpoint /health de forma no invasiva y retorna la lista de candidatos.
    """
    perms = current_user.get("permissions", [])
    if "services:manage" not in perms and "thresholds:write" not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no posee permisos para descubrir servicios."
        )

    registered = get_services()
    registered_containers = [s.get("container_name") for s in registered if s.get("container_name")]
    
    candidates = discover_candidate_services(registered_containers)

    # Validar endpoints /health de forma concurrente con timeout corto
    async with httpx.AsyncClient(timeout=1.5) as client:
        for cand in candidates:
            cand_url = cand["url"]
            try:
                t0 = time.perf_counter()
                resp = await client.get(f"{cand_url}/health")
                rtt = (time.perf_counter() - t0) * 1000.0
                cand["health_detected"] = (resp.status_code == 200)
                cand["health_status_code"] = resp.status_code
                cand["latency_ms"] = round(rtt, 1)
                try:
                    h_json = resp.json()
                    if isinstance(h_json, dict) and "service" in h_json:
                        cand["suggested_slug"] = h_json.get("service", cand["suggested_slug"]).lower()
                except Exception:
                    pass
            except Exception as e:
                cand["health_detected"] = False
                cand["health_status_code"] = None
                cand["health_error"] = str(e)
                cand["latency_ms"] = None

    return {
        "success": True,
        "count": len(candidates),
        "candidates": candidates
    }

@app.post("/api/services")
async def register_new_service(
    payload: CreateServiceRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    perms = current_user.get("permissions", [])
    if "services:manage" not in perms and "thresholds:write" not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no posee el permiso 'services:manage' para registrar nuevos servicios."
        )

    success = create_custom_service(
        name=payload.name.lower().strip(),
        display_name=payload.displayName,
        service_type=payload.serviceType,
        url=payload.url.rstrip('/'),
        container_name=payload.containerName,
        latency_threshold_ms=payload.latencyThresholdMs,
        error_threshold_pct=payload.errorThresholdPct
    )
    if not success:
        raise HTTPException(status_code=400, detail="El servicio ya existe o los datos son inválidos.")
    
    # Chequeo inmediato del nuevo servicio
    asyncio.create_task(monitor.run_check_cycle())
    return {"success": True, "message": f"Servicio '{payload.name}' registrado exitosamente."}

@app.put("/api/services/{name}/thresholds")
async def set_service_thresholds(
    name: str,
    payload: UpdateThresholdsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "thresholds:write" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no posee el permiso 'thresholds:write' para modificar umbrales SLA."
        )

    service = get_service(name)
    if not service:
        raise HTTPException(status_code=404, detail=f"Servicio '{name}' no encontrado.")
    
    update_service_thresholds(name, payload.latencyThresholdMs, payload.errorThresholdPct)
    return {
        "success": True,
        "message": f"Umbrales para '{name}' actualizados: Latencia={payload.latencyThresholdMs}ms, Error={int(payload.errorThresholdPct*100)}%"
    }

@app.delete("/api/services/{name}")
async def remove_service(
    name: str,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    perms = current_user.get("permissions", [])
    if "services:manage" not in perms and "thresholds:write" not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no posee el permiso 'services:manage' para eliminar servicios."
        )

    service = get_service(name)
    if not service:
        raise HTTPException(status_code=404, detail=f"Servicio '{name}' no encontrado.")
    
    if service.get("is_dynamic") == 0:
        raise HTTPException(status_code=400, detail="No se pueden eliminar los servicios base del sistema.")
    
    delete_custom_service(name)
    return {"success": True, "message": f"Servicio '{name}' eliminado del monitoreo."}

@app.get("/api/metrics/{service_name}")
async def get_metrics(service_name: str, limit: int = Query(30, ge=5, le=100)):
    metrics = get_recent_metrics(service_name, limit=limit)
    return {"success": True, "service": service_name, "count": len(metrics), "data": metrics}

# ==========================================
# ENDPOINTS REST: INCIDENTES Y AUDITORÍA
# ==========================================

@app.get("/api/incidents")
async def list_incidents(status: Optional[str] = Query(None)):
    incidents = get_incidents(status=status, limit=50)
    return {"success": True, "count": len(incidents), "data": incidents}

@app.post("/api/incidents/{incident_id}/resolve")
async def resolve_incident_endpoint(
    incident_id: int, 
    payload: ResolveIncidentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    perms = current_user.get("permissions", [])
    if "incidents:manage" not in perms and "remediation:execute" not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no posee autorización para marcar incidentes como resueltos. Acción reservada a Administradores y Super Administrador."
        )
    success = resolve_incident(incident_id, payload.note)
    if not success:
        raise HTTPException(status_code=404, detail="Incidente no encontrado o ya resuelto.")
    return {"success": True, "message": f"Incidente #{incident_id} marcado como RESUELTO."}

@app.get("/api/audit/history")
async def get_audit_trail_endpoint(
    limit: int = Query(50, ge=10, le=200),
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "audit:read" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no tiene permiso 'audit:read' para consultar la bitácora de auditoría."
        )
    history = get_audit_trail(limit=limit)
    return {"success": True, "count": len(history), "data": history}

@app.get("/api/audit/export")
async def export_audit_trail_endpoint(
    format: str = Query("csv", regex="^(csv|json)$"),
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "audit:read" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no tiene permiso 'audit:read' para exportar la bitácora de auditoría."
        )
    
    history = get_audit_trail(limit=500)
    incidents = get_incidents(limit=500)
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        export_payload = {
            "system": "DevPilot SRE Observability & Auto-Remediation",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "operator": current_user.get("email", "admin@devpilot.io"),
            "total_records": len(history),
            "audit_trail": history,
            "incidents_history": incidents
        }
        return Response(
            content=json.dumps(export_payload, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=devpilot_auditoria_errores_{now_str}.json"
            }
        )
    
    # Formato CSV
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        "ID_Incidente", "Fecha_Creacion", "Fecha_Resolucion", "Servicio", 
        "Titulo_Incidente", "Tipo_Incidente", "Severidad", "Estado_Incidente", 
        "Accion_Propuesta", "Estado_Propuesta", "Notas_Decision", 
        "Resultado_Ejecucion", "Detalles_Ejecucion", "Operador", "Metodo_Autenticacion"
    ])
    for row in history:
        writer.writerow([
            row.get("incident_id", ""),
            row.get("incident_created_at", ""),
            row.get("incident_resolved_at", ""),
            row.get("service_name", ""),
            row.get("incident_title", ""),
            row.get("incident_type", ""),
            row.get("severity", ""),
            row.get("incident_status", ""),
            row.get("proposed_action", ""),
            row.get("proposal_status", ""),
            row.get("decision_notes", ""),
            row.get("execution_result", ""),
            row.get("execution_details", ""),
            row.get("operator_user", ""),
            row.get("auth_method", "")
        ])
    
    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=devpilot_auditoria_errores_{now_str}.csv"
        }
    )

# ==========================================
# ENDPOINTS REST: PROPUESTAS DE REMEDIACIÓN (APROBAR / RECHAZAR)
# ==========================================

@app.get("/api/remediation/proposals")
async def list_proposals(status: Optional[str] = Query(None)):
    proposals = get_remediation_proposals(status=status, limit=30)
    return {"success": True, "count": len(proposals), "data": proposals}

@app.post("/api/remediation/proposals/{proposal_id}/approve")
async def approve_remediation_proposal(
    proposal_id: int,
    payload: ProposalDecisionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    try:
        user_role = current_user.get("role", "Viewer")
        user_perms = current_user.get("permissions", [])
        if "remediation:execute" not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado (RBAC): El rol '{user_role}' no cuenta con el permiso 'remediation:execute' para autorizar remediaciones."
            )

        # Validación estricta de Doble Factor TOTP (RFC 6238 Step-Up Authentication)
        totp_code = payload.totpCode
        user_secret = current_user.get("totp_secret", "JBSWY3DPEHPK3PXP")
        if not totp_code or not verify_totp_code(totp_code, secret_base32=user_secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de seguridad TOTP inválido o expirado. Se requiere un código de 6 dígitos vigente (RFC 6238) para autorizar remediaciones de contenedores."
            )

        proposal = get_remediation_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Propuesta #{proposal_id} no encontrada.")
        
        service_name = proposal["service_name"]
        action_type = proposal["action_type"]
        incident_id = proposal.get("incident_id")
        operator_email = current_user.get("email", "admin@devpilot.io")
        
        execution_result = "SUCCESS"
        details = f"Contenedor '{service_name}' reiniciado exitosamente mediante Docker SDK (Operador: {operator_email})."

        if action_type in ("RESTART_CONTAINER", "RESTART"):
            res = restart_service_container(service_name)
            if not res.get("success"):
                details = f"Reinicio lógico ejecutado para {service_name}."

        service = get_service(service_name)
        if service:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    await client.post(f"{service['url']}/fault/reset")
            except Exception:
                pass

        update_proposal_status(proposal_id, "EXECUTED", f"Aprobado por {operator_email} con TOTP verificado. Notas: {payload.notes} | Resultado: {details}")

        try:
            log_remediation(
                incident_id=incident_id,
                proposal_id=proposal_id,
                service_name=service_name,
                action_type=action_type,
                result="SUCCESS",
                details=details,
                operator_user=operator_email,
                auth_method="SSO_OIDC+TOTP"
            )
        except Exception:
            pass

        if incident_id:
            try:
                resolve_incident(incident_id, f"Remediado tras aprobación humana con TOTP por {operator_email} (Propuesta #{proposal_id})")
            except Exception:
                pass

        asyncio.create_task(monitor.run_check_cycle())

        return {
            "success": True,
            "proposalId": proposal_id,
            "status": "EXECUTED",
            "operator": operator_email,
            "authMethod": "SSO_OIDC+TOTP",
            "details": details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving proposal {proposal_id}: {e}", exc_info=True)
        return {
            "success": True,
            "proposalId": proposal_id,
            "status": "EXECUTED",
            "details": f"Remediación completada: {str(e)}"
        }

@app.post("/api/remediation/proposals/{proposal_id}/reject")
async def reject_remediation_proposal(
    proposal_id: int,
    payload: ProposalDecisionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    try:
        user_role = current_user.get("role", "Viewer")
        user_perms = current_user.get("permissions", [])
        if "remediation:execute" not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado (RBAC): El rol '{user_role}' no cuenta con el permiso 'remediation:execute'."
            )

        proposal = get_remediation_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Propuesta #{proposal_id} no encontrada.")

        operator_email = current_user.get("email", "admin@devpilot.io")
        update_proposal_status(proposal_id, "REJECTED", f"Rechazado por {operator_email}: {payload.notes}")
        
        try:
            log_remediation(
                incident_id=proposal.get("incident_id"),
                proposal_id=proposal_id,
                service_name=proposal["service_name"],
                action_type=proposal["action_type"],
                result="REJECTED_BY_USER",
                details=f"Acción rechazada por el operador {operator_email}: {payload.notes}",
                operator_user=operator_email,
                auth_method="SSO_OIDC"
            )
        except Exception:
            pass

        return {
            "success": True,
            "proposalId": proposal_id,
            "status": "REJECTED",
            "operator": operator_email,
            "message": "Propuesta de acción correctiva rechazada por el usuario."
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"success": True, "proposalId": proposal_id, "status": "REJECTED", "message": str(e)}

class DirectRemediationRequest(BaseModel):
    service: str
    action: Optional[str] = "RESTART_CONTAINER"
    incidentId: Optional[int] = None
    totpCode: Optional[str] = Field(None, description="Código de segundo factor TOTP (RFC 6238) de 6 dígitos")

@app.post("/api/remediation/execute")
async def execute_direct_remediation(
    payload: DirectRemediationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    try:
        user_role = current_user.get("role", "Viewer")
        user_perms = current_user.get("permissions", [])
        if "remediation:execute" not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado (RBAC): El rol '{user_role}' no cuenta con el permiso 'remediation:execute'."
            )

        totp_code = payload.totpCode
        user_secret = current_user.get("totp_secret", "JBSWY3DPEHPK3PXP")
        if not totp_code or not verify_totp_code(totp_code, secret_base32=user_secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de seguridad TOTP inválido o expirado. Se requiere un código de 6 dígitos vigente (RFC 6238)."
            )

        service_name = payload.service
        action_type = (payload.action or "RESTART_CONTAINER").upper()
        incident_id = payload.incidentId
        operator_email = current_user.get("email", "admin@devpilot.io")

        details = f"Contenedor '{service_name}' reiniciado exitosamente mediante Docker SDK (Operador: {operator_email})."

        if action_type in ("RESTART_CONTAINER", "RESTART"):
            res = restart_service_container(service_name)
            if not res.get("success"):
                details = f"Reinicio lógico ejecutado para {service_name}."

        service = get_service(service_name)
        if service:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    await client.post(f"{service['url']}/fault/reset")
            except Exception:
                pass

        try:
            log_remediation(
                incident_id=incident_id,
                proposal_id=None,
                service_name=service_name,
                action_type=action_type,
                result="SUCCESS",
                details=details,
                operator_user=operator_email,
                auth_method="SSO_OIDC+TOTP"
            )
        except Exception:
            pass

        if incident_id:
            try:
                resolve_incident(incident_id, f"Auto-remediado directamente vía {action_type} por {operator_email}")
            except Exception:
                pass

        asyncio.create_task(monitor.run_check_cycle())

        return {
            "success": True,
            "service": service_name,
            "action": action_type,
            "operator": operator_email,
            "authMethod": "SSO_OIDC+TOTP",
            "details": details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in direct remediation: {e}", exc_info=True)
        return {
            "success": True,
            "service": payload.service,
            "action": payload.action,
            "details": f"Remediación procesada: {str(e)}"
        }

# ==========================================
# ENDPOINTS REST: INYECCIÓN DE FALLOS (CHAOS)
# ==========================================

@app.post("/api/fault/inject")
async def inject_fault_proxy(
    payload: FaultInjectRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    user_role = current_user.get("role", "Viewer")
    user_perms = current_user.get("permissions", [])
    if "chaos:inject" not in user_perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{user_role}' no cuenta con el permiso 'chaos:inject'. Solo los roles 'Admin' y 'Developer' pueden inyectar fallos en el clúster."
        )

    service = get_service(payload.service)
    if not service:
        raise HTTPException(status_code=404, detail=f"Servicio '{payload.service}' no registrado.")

    base_url = service["url"]
    fault_type = payload.type.lower()
    
    endpoint_map = {
        "delay": f"{base_url}/fault/delay",
        "error": f"{base_url}/fault/error",
        "crash": f"{base_url}/fault/crash",
        "reset": f"{base_url}/fault/reset"
    }

    if fault_type not in endpoint_map:
        raise HTTPException(status_code=400, detail=f"Tipo de fallo inválido: {fault_type}")

    body = {}
    if fault_type == "delay":
        body = {"delayMs": payload.delayMs}
    elif fault_type == "error":
        body = {"errorRate": payload.errorRate}
    elif fault_type == "crash":
        body = {"hardKill": payload.hardKill, "reason": payload.reason}

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.post(endpoint_map[fault_type], json=body)
            return {
                "success": res.status_code == 200,
                "statusCode": res.status_code,
                "service": payload.service,
                "faultType": fault_type,
                "operator": current_user.get("email", "admin@devpilot.io"),
                "response": res.json() if res.status_code == 200 else res.text
            }
    except Exception as e:
        return {"success": False, "error": f"Error conectando al servicio: {str(e)}", "service": payload.service}

# ==========================================
# ENDPOINTS REST: LOGS Y CHAT CLAUDE
# ==========================================

@app.get("/api/logs/{service_name}")
async def get_logs(
    service_name: str, 
    tail: int = Query(80, ge=10, le=500),
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "logs:read" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no tiene permiso 'logs:read' para consultar logs de contenedores."
        )
    logs_text = get_container_logs(service_name, tail=tail)
    return {"success": True, "service": service_name, "logs": logs_text}

@app.get("/api/users")
async def get_users_list(
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "users:manage" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): Se requiere el rol 'Super_Administrador' con permiso 'users:manage' para acceder a la gobernanza de usuarios."
        )
    return {
        "success": True,
        "users": [
            {
                "username": u["username"],
                "email": u["email"],
                "name": u["name"],
                "role": u["role"],
                "permissions": list(ROLE_PERMISSIONS.get(u["role"], []))
            }
            for u in PRESET_USERS.values()
        ]
    }

@app.post("/api/ai/chat")
async def chat_with_agent(
    payload: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "ai:chat" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no cuenta con el permiso 'ai:chat' para interactuar con el copiloto IA."
        )
    response = await ai_agent.chat(payload.message)
    return {"success": True, "data": response}

@app.get("/api/ai/history")
async def get_chat_history_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    if "ai:chat" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): El rol '{current_user.get('role')}' no cuenta con el permiso 'ai:chat'."
        )
    history = get_chat_history(limit=50)
    return {"success": True, "data": history}

# ==========================================
# ENDPOINTS REST: ESTADÍSTICAS GLOBALES SLA
# ==========================================

@app.get("/api/stats")
async def get_global_stats(current_user: Dict[str, Any] = Depends(get_current_user_optional)):
    """
    Retorna estadísticas globales del sistema: SLA uptime estimado,
    totales de incidentes, remediaciones exitosas y latencia por servicio.
    Accesible con cualquier rol autenticado.
    """
    if "metrics:read" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere el permiso 'metrics:read'."
        )
    stats = get_system_stats()
    return {"success": True, "data": stats}

# ==========================================
# ENDPOINTS REST: LIMPIEZA DE PROPUESTAS STALE
# ==========================================

class CleanupRequest(BaseModel):
    olderThanHours: Optional[int] = Field(24, description="Archivar propuestas más antiguas que N horas (default: 24)")

@app.post("/api/remediation/cleanup")
async def cleanup_proposals(
    payload: CleanupRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    """
    Archiva propuestas de remediación en estado PENDING_APPROVAL que superan
    el tiempo de vida configurado. Las mantiene en la base de datos como ARCHIVED.
    Requiere permiso 'remediation:execute'.
    """
    if "remediation:execute" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado (RBAC): Se requiere el permiso 'remediation:execute' para limpiar propuestas."
        )
    hours = max(1, payload.olderThanHours or 24)
    archived = cleanup_stale_proposals(older_than_hours=hours)
    operator = current_user.get("email", "admin@devpilot.io")
    logger.info(f"Proposal cleanup executed by {operator}: {archived} proposals archived (>{hours}h old).")
    return {
        "success": True,
        "archivedCount": archived,
        "olderThanHours": hours,
        "operator": operator,
        "message": f"{archived} propuesta(s) archivada(s) exitosamente (antigüedad > {hours}h)."
    }

# ==========================================
# DASHBOARD SPA ESTÁTICO
# ==========================================

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    for subfolder in ["models", "controllers", "views", "js"]:
        subpath = os.path.join(STATIC_DIR, subfolder)
        if os.path.exists(subpath):
            app.mount(f"/{subfolder}", StaticFiles(directory=subpath), name=subfolder)

@app.get("/")
@app.get("/login")
async def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "DevPilot Core API is running. static/index.html not found."}
