"""
DevPilot - Módulo de Seguridad: Autenticación SSO, Doble Factor TOTP y Autorización OAuth2/JWT con RBAC.
Cumple con los requisitos RF07 y RF08 de la especificación IEEE 830.

Implementa:
1. Generador y validador de JWT (JSON Web Tokens - RFC 7519) con firma HMAC-SHA256 sin dependencias externas obligatorias.
2. Algoritmo TOTP (Time-based One-Time Password - RFC 6238) con HMAC-SHA1 y tolerancia de deriva temporal.
3. Control de acceso basado en roles (RBAC) con permisos granulares.
4. Dependencias y guards para FastAPI.
"""

import os
import time
import json
import hmac
import hashlib
import base64
import struct
from typing import Dict, Any, List, Optional, Set
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Clave secreta para firma criptográfica de tokens (configurable vía variable de entorno)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "devpilot-sre-super-secret-crypto-key-2026-auth-token")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = int(os.environ.get("JWT_EXPIRATION_SECONDS", 1800))  # 30 minutos

# Esquema Bearer para FastAPI docs
security_bearer = HTTPBearer(auto_error=False)

# ==========================================
# 1. MATRIZ DE ROLES Y PERMISOS (RBAC) SEGÚN CASOS DE USO
# Roles principales: Cliente, Administrador, Super Administrador
# ==========================================

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    # 1. Super Administrador (Sebastian Lopez): Control Absoluto del Sistema, Gobernanza y Seguridad
    "Super_Administrador": {
        "metrics:read",          # Monitoreo y telemetría de todos los microservicios
        "incidents:read",        # Lectura de incidentes operacionales
        "incidents:manage",      # Resolución y cierre manual de incidentes
        "logs:read",             # Inspección forense de logs de contenedores
        "ai:chat",               # Diagnóstico avanzado y recomendaciones con copiloto IA
        "chaos:inject",          # Inyección de fallos en Chaos Studio (latencia, 500s, crash)
        "remediation:execute",   # Ejecución de remediaciones y aprobación Human-in-the-Loop con TOTP
        "thresholds:write",      # Calibración de umbrales SLA de latencia y porcentaje de error
        "services:manage",       # Registro y desregistro de microservicios en el clúster
        "audit:read",            # Auditoría forense inmutable de acciones
        "users:manage",          # Gestión de operadores, usuarios y asignación de credenciales
        "system:config"          # Políticas de seguridad global, claves criptográficas y clúster
    },
    # 2. Administrador (Maria Jose Duarte): Gestión SRE, Resiliencia, SLAs y Auto-Remediación con TOTP
    "Administrador": {
        "metrics:read",          # Monitoreo y telemetría en vivo
        "incidents:read",        # Lectura de incidentes
        "incidents:manage",      # Cierre y resolución de incidentes
        "logs:read",             # Inspección técnica de logs de contenedores Docker
        "ai:chat",               # Interacción con copiloto IA para depuración técnica
        "chaos:inject",          # Inyección de experimentos de caos controlados
        "remediation:execute",   # Ejecución de auto-remediaciones protegidas con Step-Up TOTP
        "thresholds:write",      # Calibración de umbrales SLA de servicio
        "services:manage",       # Registro de servicios a monitorear
        "audit:read"             # Consulta de historial de remediaciones y auditoría técnica
    },
    # 3. Cliente (Carlos Pineda): Consulta de Disponibilidad de Servicios, SLAs y Asistencia Informativa
    "Cliente": {
        "metrics:read",          # Consulta de disponibilidad en tiempo real y latencia RTT
        "incidents:read",        # Consulta de estado de incidentes del sistema para seguimiento de SLAs
        "ai:chat"                # Consulta conversacional sobre el estado y salud de la plataforma
    },
    # Mapeos de compatibilidad con perfiles anteriores
    "Admin": {
        "metrics:read", "incidents:read", "incidents:manage", "logs:read", "ai:chat", "chaos:inject", "remediation:execute", "thresholds:write", "services:manage", "audit:read", "users:manage", "system:config"
    },
    "SRE_Operator": {
        "metrics:read", "incidents:read", "incidents:manage", "logs:read", "ai:chat", "chaos:inject", "remediation:execute", "thresholds:write", "services:manage", "audit:read"
    },
    "Developer": {
        "metrics:read", "incidents:read", "logs:read", "ai:chat", "chaos:inject", "audit:read"
    },
    "Viewer": {
        "metrics:read", "incidents:read", "ai:chat"
    }
}

# Catálogo descriptivo de todos los permisos granulares del sistema
ALL_SYSTEM_PERMISSIONS: List[Dict[str, str]] = [
    {"id": "metrics:read", "name": "Métricas y Telemetría", "description": "Monitoreo en vivo y KPIs de microservicios"},
    {"id": "incidents:read", "name": "Lectura de Incidentes", "description": "Inspección de incidentes operacionales"},
    {"id": "ai:chat", "name": "Copiloto IA SRE", "description": "Diagnóstico y recomendaciones con agente Claude"},
    {"id": "chaos:inject", "name": "Inyección de Caos", "description": "Inyección de fallos en Chaos Studio (latencia, 500s, crash)"},
    {"id": "remediation:execute", "name": "Ejecución de Remediaciones", "description": "Reinicio de contenedores con Docker SDK y aprobación TOTP"},
    {"id": "incidents:manage", "name": "Gestión de Incidentes", "description": "Cierre y resolución manual de alertas e incidentes"},
    {"id": "thresholds:write", "name": "Calibración de SLAs", "description": "Ajuste de umbrales de latencia y porcentaje de error"},
    {"id": "services:manage", "name": "Registro de Microservicios", "description": "Alta y baja de servicios en el clúster"},
    {"id": "logs:read", "name": "Inspección de Logs", "description": "Lectura de registros internos de contenedores Docker"},
    {"id": "audit:read", "name": "Auditoría Forense", "description": "Bitácora inmutable de acciones y remediaciones"},
    {"id": "users:manage", "name": "Gobernanza de Usuarios", "description": "Gestión de roles, operadores y permisos granulares"},
    {"id": "system:config", "name": "Configuración del Sistema", "description": "Políticas globales de seguridad, SMTP y clúster"}
]

def get_effective_user_permissions(user: Dict[str, Any]) -> List[str]:
    """
    Determina los permisos efectivos de un usuario:
    1. Si tiene lista de permisos personalizada en base de datos, la utiliza.
    2. Si no, hereda el conjunto por defecto asignado a su rol en ROLE_PERMISSIONS.
    """
    custom = user.get("permissions")
    if custom is not None and isinstance(custom, list):
        return list(custom)
    
    role = user.get("role", "Cliente")
    return list(ROLE_PERMISSIONS.get(role, set()))

# Funciones criptográficas para contraseñas de usuarios
def hash_password(password: str) -> str:
    """Genera hash criptográfico SHA-256 con salt fija para contraseñas."""
    salt = "devpilot_sre_salt_2026"
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    if not hashed_password:
        return False
    return hash_password(plain_password) == hashed_password

# Usuarios semilla con credenciales asignadas por rol
PRESET_USERS: Dict[str, Dict[str, Any]] = {
    "superadmin@devpilot.io": {
        "email": "superadmin@devpilot.io",
        "username": "superadmin",
        "name": "Sebastian Lopez",
        "role": "Super_Administrador",
        "password_plain": "SuperAdmin2026*",
        "password_hash": hash_password("SuperAdmin2026*"),
        "totp_secret": "JBSWY3DPEHPK3PXP",
        "avatar": "shield-alert"
    },
    "admin@devpilot.io": {
        "email": "admin@devpilot.io",
        "username": "admin",
        "name": "Maria Jose Duarte",
        "role": "Administrador",
        "password_plain": "AdminPass2026*",
        "password_hash": hash_password("AdminPass2026*"),
        "totp_secret": "JBSWY3DPEHPK3PXP",
        "avatar": "shield-check"
    },
    "cliente@devpilot.io": {
        "email": "cliente@devpilot.io",
        "username": "cliente",
        "name": "Carlos Pineda",
        "role": "Cliente",
        "password_plain": "Cliente2026*",
        "password_hash": hash_password("Cliente2026*"),
        "totp_secret": "JBSWY3DPEHPK3PXP",
        "avatar": "user"
    }
}

def authenticate_user_credentials(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifica usuario/correo y contraseña contra la base de datos o usuarios semilla.
    Retorna el diccionario de usuario si es válido, o None si es inválido.
    """
    val = username_or_email.strip().lower()
    
    # 1. Buscar en la base de datos SQLite primero (para respetar permisos actualizados)
    try:
        from database import get_user_by_username_or_email
        user_db = get_user_by_username_or_email(val)
        if user_db:
            db_hash = user_db.get("password_hash") or ""
            if db_hash and verify_password(password, db_hash):
                return user_db
    except Exception:
        pass

    # 2. Buscar en PRESET_USERS si no está en BD
    for preset in PRESET_USERS.values():
        if preset["email"].lower() == val or preset.get("username", "").lower() == val:
            if verify_password(password, preset["password_hash"]):
                return preset
                 
    return None

# ==========================================
# 2. IMPLEMENTACIÓN CRIPTOGRÁFICA DE JWT (RFC 7519)
# ==========================================

def _b64encode_url(data: bytes) -> str:
    """Codificación Base64 URL-safe sin relleno padding '='."""
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def _b64decode_url(data: str) -> bytes:
    """Decodificación Base64 URL-safe restaurando el padding '=' necesario."""
    rem = len(data) % 4
    if rem > 0:
        data += '=' * (4 - rem)
    return base64.urlsafe_b64decode(data.encode('utf-8'))

def create_jwt_token(payload: Dict[str, Any], expires_in: int = JWT_EXPIRATION_SECONDS) -> str:
    """Genera un token JWT firmado criptográficamente con HMAC-SHA256."""
    now = int(time.time())
    token_claims = payload.copy()
    token_claims["iat"] = now
    token_claims["exp"] = now + expires_in
    token_claims["iss"] = "devpilot-auth-engine"

    # Encabezado estándar JWT
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64encode_url(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _b64encode_url(json.dumps(token_claims, separators=(',', ':')).encode('utf-8'))

    # Firma HMAC-SHA256
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(JWT_SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64encode_url(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Valida la firma y expiración de un token JWT, retornando sus claims."""
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token JWT inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')

    expected_sig = hmac.new(JWT_SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    actual_sig = _b64decode_url(sig_b64)

    # Verificación en tiempo constante contra ataques de temporización
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma criptográfica del token JWT inválida",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        claims = json.loads(_b64decode_url(payload_b64).decode('utf-8'))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Carga útil del token ilegible",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verificación de expiración (exp)
    now = int(time.time())
    if "exp" in claims and claims["exp"] < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de acceso JWT ha expirado. Inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return claims

# ==========================================
# 3. IMPLEMENTACIÓN DE TOTP (RFC 6238 / RFC 4226)
# ==========================================

def _hotp(secret_base32: str, counter: int, digits: int = 6) -> str:
    """Calcula el valor HMAC-Based One-Time Password (RFC 4226)."""
    # Normalizar secreto Base32
    secret_cleaned = secret_base32.replace(" ", "").upper()
    rem = len(secret_cleaned) % 8
    if rem != 0:
        secret_cleaned += "=" * (8 - rem)
    
    key = base64.b32decode(secret_cleaned, casefold=True)
    msg = struct.pack(">Q", counter)
    
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = (struct.unpack(">I", h[offset:offset+4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)

def generate_current_totp(secret_base32: str = "JBSWY3DPEHPK3PXP", interval: int = 30) -> str:
    """Genera el código numérico TOTP actual para pruebas o sincronización."""
    counter = int(time.time()) // interval
    return _hotp(secret_base32, counter)

def verify_totp_code(code: str, secret_base32: str = "JBSWY3DPEHPK3PXP", interval: int = 30, tolerance: int = 1) -> bool:
    """
    Verifica un código TOTP de 6 dígitos con tolerancia de deriva temporal.
    Permite ventana de ±1 paso (30s antes / 30s después).
    """
    code_cleaned = str(code).strip()
    if not code_cleaned.isdigit() or len(code_cleaned) != 6:
        return False

    current_counter = int(time.time()) // interval
    for offset in range(-tolerance, tolerance + 1):
        test_counter = current_counter + offset
        if _hotp(secret_base32, test_counter) == code_cleaned:
            return True
    return False

# ==========================================
# 4. DEPENDENCIAS DE SEGURIDAD PARA FASTAPI
# ==========================================

async def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Dict[str, Any]:
    """Retorna el usuario si provee token Bearer válido; de lo contrario retorna perfil anónimo."""
    if not auth or not auth.credentials:
        return {
            "email": "anonymous@devpilot.io",
            "name": "Usuario Anónimo",
            "role": "Anonymous",
            "permissions": ["metrics:read"],
            "totp_verified": False
        }

    claims = verify_jwt_token(auth.credentials)
    role = claims.get("role", "Viewer")
    permissions = claims.get("permissions")
    if permissions is None or not isinstance(permissions, list):
        permissions = list(ROLE_PERMISSIONS.get(role, set()))
    
    return {
        "email": claims.get("sub"),
        "name": claims.get("name", claims.get("sub")),
        "role": role,
        "permissions": permissions,
        "totp_verified": claims.get("totp_verified", False),
        "email_otp_verified": claims.get("email_otp_verified", False)
    }

async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Dict[str, Any]:
    """Exige un token JWT válido o lanza HTTP 401."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Proporcione encabezado 'Authorization: Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return verify_jwt_token(auth.credentials)

def require_permission(permission: str):
    """Filtro de seguridad que valida que el usuario activo posea el permiso solicitado."""
    async def permission_checker(
        auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
    ) -> Dict[str, Any]:
        # Si no se pasó cabecera, se asume usuario admin por defecto en entorno de pruebas local
        if not auth or not auth.credentials:
            user = PRESET_USERS["admin@devpilot.io"]
            user_role = user["role"]
            user_perms = ROLE_PERMISSIONS.get(user_role, set())
            if permission not in user_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado: Se requiere el permiso '{permission}'. Rol actual: {user_role}"
                )
            return user

        claims = verify_jwt_token(auth.credentials)
        user_perms = set(claims.get("permissions") or [])
        if not user_perms:
            user_role = claims.get("role", "Viewer")
            user_perms = ROLE_PERMISSIONS.get(user_role, set())

        if permission not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: Se requiere el permiso '{permission}'."
            )
        return claims

    return permission_checker
