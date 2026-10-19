import os
import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_PATH = os.environ.get("DB_PATH", "devpilot.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla de servicios monitoreados con umbrales configurables por servicio (Req 2.3.1 Admin)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            name TEXT PRIMARY KEY,
            display_name TEXT,
            service_type TEXT,
            url TEXT,
            container_name TEXT,
            status TEXT DEFAULT 'UNKNOWN',
            last_latency REAL DEFAULT 0,
            avg_latency REAL DEFAULT 0,
            error_rate REAL DEFAULT 0,
            last_check TEXT,
            uptime_seconds INTEGER DEFAULT 0,
            active_faults TEXT DEFAULT '{}',
            latency_threshold_ms REAL DEFAULT 2000.0,
            error_threshold_pct REAL DEFAULT 0.20,
            is_dynamic INTEGER DEFAULT 0
        )
    ''')

    # Migración de columnas de umbrales si ya existía la tabla
    cursor.execute("PRAGMA table_info(services)")
    columns = [row[1] for row in cursor.fetchall()]
    if "latency_threshold_ms" not in columns:
        cursor.execute("ALTER TABLE services ADD COLUMN latency_threshold_ms REAL DEFAULT 2000.0")
    if "error_threshold_pct" not in columns:
        cursor.execute("ALTER TABLE services ADD COLUMN error_threshold_pct REAL DEFAULT 0.20")
    if "is_dynamic" not in columns:
        cursor.execute("ALTER TABLE services ADD COLUMN is_dynamic INTEGER DEFAULT 0")

    # Tabla de métricas históricas de salud
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT,
            status_code INTEGER,
            latency_ms REAL,
            is_error INTEGER,
            timestamp TEXT,
            FOREIGN KEY (service_name) REFERENCES services (name) ON DELETE CASCADE
        )
    ''')

    # Tabla de incidentes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT,
            title TEXT,
            description TEXT,
            simple_explanation TEXT,
            incident_type TEXT,
            severity TEXT,
            status TEXT DEFAULT 'OPEN',
            latency_ms REAL,
            error_rate REAL,
            logs_sample TEXT,
            ai_recommendation TEXT,
            created_at TEXT,
            resolved_at TEXT,
            FOREIGN KEY (service_name) REFERENCES services (name) ON DELETE CASCADE
        )
    ''')

    # Migración de simple_explanation si no existe
    cursor.execute("PRAGMA table_info(incidents)")
    inc_columns = [row[1] for row in cursor.fetchall()]
    if "simple_explanation" not in inc_columns:
        cursor.execute("ALTER TABLE incidents ADD COLUMN simple_explanation TEXT DEFAULT ''")

    # Tabla de propuestas de remediación con Aprobación/Rechazo del usuario (Req 2.2 / 2.3.1 Human-in-the-loop)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remediation_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            service_name TEXT,
            action_type TEXT,
            reason TEXT,
            simple_explanation TEXT,
            status TEXT DEFAULT 'PENDING_APPROVAL',
            created_at TEXT,
            decided_at TEXT,
            decision_notes TEXT,
            FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE SET NULL,
            FOREIGN KEY (service_name) REFERENCES services (name) ON DELETE CASCADE
        )
    ''')

    # Tabla de logs de auditoría forense de remediaciones ejecutadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remediation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER,
            proposal_id INTEGER,
            service_name TEXT,
            action_type TEXT,
            result TEXT,
            details TEXT,
            timestamp TEXT,
            operator_user TEXT DEFAULT 'admin@devpilot.io',
            auth_method TEXT DEFAULT 'SSO_OIDC+TOTP',
            FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE SET NULL,
            FOREIGN KEY (proposal_id) REFERENCES remediation_proposals (id) ON DELETE SET NULL
        )
    ''')

    # Migraciones PRAGMA para asegurar compatibilidad total con bases de datos previas
    cursor.execute("PRAGMA table_info(remediation_logs)")
    log_cols = [row[1] for row in cursor.fetchall()]
    if "proposal_id" not in log_cols:
        try: cursor.execute("ALTER TABLE remediation_logs ADD COLUMN proposal_id INTEGER")
        except Exception: pass
    if "operator_user" not in log_cols:
        try: cursor.execute("ALTER TABLE remediation_logs ADD COLUMN operator_user TEXT DEFAULT 'admin@devpilot.io'")
        except Exception: pass
    if "auth_method" not in log_cols:
        try: cursor.execute("ALTER TABLE remediation_logs ADD COLUMN auth_method TEXT DEFAULT 'SSO_OIDC+TOTP'")
        except Exception: pass

    cursor.execute("PRAGMA table_info(remediation_proposals)")
    prop_cols = [row[1] for row in cursor.fetchall()]
    if "simple_explanation" not in prop_cols:
        try: cursor.execute("ALTER TABLE remediation_proposals ADD COLUMN simple_explanation TEXT DEFAULT ''")
        except Exception: pass
    if "decision_notes" not in prop_cols:
        try: cursor.execute("ALTER TABLE remediation_proposals ADD COLUMN decision_notes TEXT DEFAULT ''")
        except Exception: pass

    cursor.execute("PRAGMA table_info(incidents)")
    inc_cols = [row[1] for row in cursor.fetchall()]
    if "simple_explanation" not in inc_cols:
        try: cursor.execute("ALTER TABLE incidents ADD COLUMN simple_explanation TEXT DEFAULT ''")
        except Exception: pass
    if "ai_recommendation" not in inc_cols:
        try: cursor.execute("ALTER TABLE incidents ADD COLUMN ai_recommendation TEXT DEFAULT ''")
        except Exception: pass
    if "logs_sample" not in inc_cols:
        try: cursor.execute("ALTER TABLE incidents ADD COLUMN logs_sample TEXT DEFAULT ''")
        except Exception: pass

    # Tabla del historial de chat con el agente de IA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            tool_calls TEXT DEFAULT '[]',
            timestamp TEXT
        )
    ''')

    # Tabla de Usuarios para Autenticación y control RBAC (Requisitos RF07, RF08)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            name TEXT,
            role TEXT,
            password_hash TEXT,
            totp_secret TEXT,
            created_at TEXT,
            last_login TEXT
        )
    ''')

    # Tabla de Códigos OTP de Correo Electrónico (MFA Email)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("PRAGMA table_info(users)")
    u_cols = [row[1] for row in cursor.fetchall()]
    if "password_hash" not in u_cols:
        try: cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT ''")
        except Exception: pass
    if "username" not in u_cols:
        try: cursor.execute("ALTER TABLE users ADD COLUMN username TEXT DEFAULT ''")
        except Exception: pass
    if "permissions" not in u_cols:
        try: cursor.execute("ALTER TABLE users ADD COLUMN permissions TEXT DEFAULT ''")
        except Exception: pass

    def _hp(p: str) -> str:
        return hashlib.sha256(("devpilot_sre_salt_2026" + p).encode('utf-8')).hexdigest()

    now_iso = datetime.now(timezone.utc).isoformat()
    seed_users = [
        ("superadmin@devpilot.io", "superadmin", "Sebastian Lopez", "Super_Administrador", _hp("SuperAdmin2026*"), "JBSWY3DPEHPK3PXP"),
        ("admin@devpilot.io", "admin", "Maria Jose Duarte", "Administrador", _hp("AdminPass2026*"), "JBSWY3DPEHPK3PXP"),
        ("cliente@devpilot.io", "cliente", "Carlos Pineda", "Cliente", _hp("Cliente2026*"), "JBSWY3DPEHPK3PXP")
    ]
    for email, uname, rname, urole, phash, usecret in seed_users:
        cursor.execute('''
            INSERT INTO users (email, username, name, role, password_hash, totp_secret, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET 
                username=excluded.username,
                name=excluded.name, 
                role=excluded.role, 
                password_hash=excluded.password_hash, 
                totp_secret=excluded.totp_secret
        ''', (email, uname, rname, urole, phash, usecret, now_iso))

    # Sembrar servicios predeterminados
    default_services = [
        ("users", "Users Service (Node.js/Express)", "Node.js", "http://users_service:3001", "devpilot_users", 2000.0, 0.20),
        ("products", "Products Service (FastAPI)", "Python", "http://products_service:3002", "devpilot_products", 2000.0, 0.20),
        ("orders", "Orders Service (FastAPI)", "Python", "http://orders_service:3003", "devpilot_orders", 2000.0, 0.20)
    ]

    for name, dname, stype, url, container, lat_thr, err_thr in default_services:
        cursor.execute('''
            INSERT OR IGNORE INTO services (name, display_name, service_type, url, container_name, status, last_check, latency_threshold_ms, error_threshold_pct, is_dynamic)
            VALUES (?, ?, ?, ?, ?, 'HEALTHY', ?, ?, ?, 0)
        ''', (name, dname, stype, url, container, datetime.now(timezone.utc).isoformat(), lat_thr, err_thr))

    # Asegurar que servicios base inicien con estado limpio
    cursor.execute("UPDATE services SET status = 'HEALTHY' WHERE status = 'UNKNOWN'")

    conn.commit()
    conn.close()

# ==========================================
# SERVICIOS Y UMBRALES (Historias 3 y 4)
# ==========================================

def normalize_service_url(url: str) -> str:
    """
    Normaliza la URL de un microservicio.
    Si se ejecuta de forma nativa/standalone fuera de Docker, resuelve
    los alias de contenedor de red Docker (users_service, etc.) a 127.0.0.1.
    """
    if not os.path.exists("/.dockerenv") and not os.environ.get("RUNNING_IN_DOCKER"):
        for alias in ["users_service", "products_service", "orders_service", "payments_service"]:
            if alias in url:
                return url.replace(alias, "127.0.0.1")
    return url

def get_services() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services ORDER BY name ASC')
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if "url" in d and d["url"]:
            d["url"] = normalize_service_url(d["url"])
        result.append(d)
    return result

def get_service(name: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if "url" in d and d["url"]:
        d["url"] = normalize_service_url(d["url"])
    return d

def create_custom_service(name: str, display_name: str, service_type: str, url: str, container_name: str, latency_threshold_ms: float = 2000.0, error_threshold_pct: float = 0.20) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    try:
        cursor.execute('''
            INSERT INTO services (name, display_name, service_type, url, container_name, status, last_check, latency_threshold_ms, error_threshold_pct, is_dynamic)
            VALUES (?, ?, ?, ?, ?, 'UNKNOWN', ?, ?, ?, 1)
        ''', (name, display_name, service_type, url, container_name, now, latency_threshold_ms, error_threshold_pct))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_service_thresholds(service_name: str, latency_threshold_ms: float, error_threshold_pct: float) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE services
        SET latency_threshold_ms = ?, error_threshold_pct = ?
        WHERE name = ?
    ''', (latency_threshold_ms, error_threshold_pct, service_name))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_custom_service(service_name: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE name = ?', (service_name,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def upsert_service_status(
    name: str,
    status: str,
    last_latency: float,
    avg_latency: float,
    error_rate: float,
    uptime_seconds: int = 0,
    active_faults: str = "{}"
):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        UPDATE services
        SET status = ?, last_latency = ?, avg_latency = ?, error_rate = ?, last_check = ?, uptime_seconds = ?, active_faults = ?
        WHERE name = ?
    ''', (status, last_latency, avg_latency, error_rate, now, uptime_seconds, active_faults, name))
    conn.commit()
    conn.close()

# ==========================================
# MÉTRICAS E INCIDENTES
# ==========================================

def insert_health_metric(service_name: str, status_code: int, latency_ms: float, is_error: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        INSERT INTO health_metrics (service_name, status_code, latency_ms, is_error, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (service_name, status_code, latency_ms, 1 if is_error else 0, now))
    
    cursor.execute('''
        DELETE FROM health_metrics 
        WHERE id IN (
            SELECT id FROM health_metrics 
            WHERE service_name = ? 
            ORDER BY id DESC LIMIT -1 OFFSET 500
        )
    ''', (service_name,))
    
    conn.commit()
    conn.close()

def get_recent_metrics(service_name: str, limit: int = 30) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, service_name, status_code, latency_ms, is_error, timestamp
        FROM health_metrics
        WHERE service_name = ?
        ORDER BY id DESC
        LIMIT ?
    ''', (service_name, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def get_open_incident_for_service(service_name: str, incident_type: str = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if incident_type:
        cursor.execute('''
            SELECT * FROM incidents
            WHERE service_name = ? AND status = 'OPEN' AND incident_type = ?
            ORDER BY id DESC LIMIT 1
        ''', (service_name, incident_type))
    else:
        cursor.execute('''
            SELECT * FROM incidents
            WHERE service_name = ? AND status = 'OPEN'
            ORDER BY id DESC LIMIT 1
        ''', (service_name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_incident(
    service_name: str,
    title: str,
    description: str,
    incident_type: str,
    severity: str,
    latency_ms: float = 0,
    error_rate: float = 0,
    logs_sample: str = "",
    ai_recommendation: str = "",
    simple_explanation: str = ""
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        INSERT INTO incidents (
            service_name, title, description, simple_explanation, incident_type, severity, status,
            latency_ms, error_rate, logs_sample, ai_recommendation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, ?)
    ''', (
        service_name, title, description, simple_explanation, incident_type, severity,
        latency_ms, error_rate, logs_sample, ai_recommendation, now
    ))
    incident_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return incident_id

def update_incident_ai_details(incident_id: int, simple_explanation: str, ai_recommendation: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE incidents
        SET simple_explanation = ?, ai_recommendation = ?
        WHERE id = ?
    ''', (simple_explanation, ai_recommendation, incident_id))
    conn.commit()
    conn.close()

def resolve_incident(incident_id: int, resolution_note: str = "") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        UPDATE incidents
        SET status = 'RESOLVED', resolved_at = ?,
            description = description || ' | ' || ?
        WHERE id = ?
    ''', (now, resolution_note, incident_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def auto_resolve_open_incidents_for_service(service_name: str, note: str = "Service recovered"):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        UPDATE incidents
        SET status = 'RESOLVED', resolved_at = ?
        WHERE service_name = ? AND status = 'OPEN'
    ''', (now, service_name))
    conn.commit()
    conn.close()

def get_incidents(status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute('''
            SELECT * FROM incidents WHERE status = ? ORDER BY id DESC LIMIT ?
        ''', (status, limit))
    else:
        cursor.execute('''
            SELECT * FROM incidents ORDER BY id DESC LIMIT ?
        ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==========================================
# PROPUESTAS DE REMEDIACIÓN Y APROBACIÓN (Historia 5)
# ==========================================

def create_remediation_proposal(
    service_name: str,
    action_type: str,
    reason: str,
    simple_explanation: str,
    incident_id: Optional[int] = None
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        INSERT INTO remediation_proposals (
            incident_id, service_name, action_type, reason, simple_explanation, status, created_at
        ) VALUES (?, ?, ?, ?, ?, 'PENDING_APPROVAL', ?)
    ''', (incident_id, service_name, action_type, reason, simple_explanation, now))
    proposal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return proposal_id

def get_remediation_proposals(status: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute('''
            SELECT * FROM remediation_proposals WHERE status = ? ORDER BY id DESC LIMIT ?
        ''', (status, limit))
    else:
        cursor.execute('''
            SELECT * FROM remediation_proposals ORDER BY id DESC LIMIT ?
        ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_remediation_proposal(proposal_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM remediation_proposals WHERE id = ?', (proposal_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_proposal_status(proposal_id: int, status: str, notes: str = "") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        UPDATE remediation_proposals
        SET status = ?, decided_at = ?, decision_notes = ?
        WHERE id = ?
    ''', (status, now, notes, proposal_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def log_remediation(
    incident_id: Optional[int] = None,
    service_name: str = "",
    action_type: str = "",
    result: str = "",
    details: str = "",
    proposal_id: Optional[int] = None,
    operator_user: str = "admin@devpilot.io",
    auth_method: str = "SSO_OIDC+TOTP"
) -> int:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute('''
            INSERT INTO remediation_logs (incident_id, proposal_id, service_name, action_type, result, details, timestamp, operator_user, auth_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (incident_id, proposal_id, service_name, action_type, result, details, now, operator_user, auth_method))
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id or 1
    except Exception as e:
        print(f"[DB WARN] Error logging remediation: {e}")
        return 1

def get_remediation_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM remediation_logs ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==========================================
# GESTIÓN DE USUARIOS Y AUTENTICACIÓN SSO
# ==========================================

def get_users() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, username, name, role, permissions, totp_secret, created_at, last_login FROM users ORDER BY id ASC')
    rows = cursor.fetchall()
    conn.close()
    users = []
    for r in rows:
        u = dict(r)
        raw_perms = u.get("permissions") or ""
        try:
            u["permissions"] = json.loads(raw_perms) if raw_perms.strip() else None
        except Exception:
            u["permissions"] = None
        users.append(u)
    return users

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE LOWER(email) = LOWER(?)', (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    u = dict(row)
    raw_perms = u.get("permissions") or ""
    try:
        u["permissions"] = json.loads(raw_perms) if raw_perms.strip() else None
    except Exception:
        u["permissions"] = None
    return u

def get_user_by_username_or_email(identifier: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    val = identifier.strip().lower()
    cursor.execute('''
        SELECT * FROM users 
        WHERE LOWER(email) = ? OR LOWER(username) = ?
    ''', (val, val))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    u = dict(row)
    raw_perms = u.get("permissions") or ""
    try:
        u["permissions"] = json.loads(raw_perms) if raw_perms.strip() else None
    except Exception:
        u["permissions"] = None
    return u

def update_user_permissions(identifier: str, permissions: Optional[List[str]]) -> bool:
    """
    Actualiza la lista de permisos personalizados para un usuario.
    Si permissions es None, se limpia la personalización para que herede las de su rol.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    val = identifier.strip().lower()
    perms_json = json.dumps(permissions) if permissions is not None else ""
    cursor.execute('''
        UPDATE users SET permissions = ? 
        WHERE LOWER(email) = ? OR LOWER(username) = ? OR CAST(id AS TEXT) = ?
    ''', (perms_json, val, val, val))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def update_user_last_login(email: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('UPDATE users SET last_login = ? WHERE LOWER(email) = LOWER(?)', (now, email.strip()))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# ==========================================
# HISTORIAL DE AUDITORÍA Y CHAT
# ==========================================

def get_audit_trail(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            i.id as incident_id,
            i.service_name,
            i.title as incident_title,
            i.incident_type,
            i.severity,
            i.created_at as incident_created_at,
            i.resolved_at as incident_resolved_at,
            i.status as incident_status,
            p.id as proposal_id,
            p.action_type as proposed_action,
            p.status as proposal_status,
            p.decision_notes,
            p.decided_at,
            l.result as execution_result,
            l.details as execution_details,
            COALESCE(l.operator_user, 'admin@devpilot.io') as operator_user,
            COALESCE(l.auth_method, 'SSO_OIDC+TOTP') as auth_method
        FROM incidents i
        LEFT JOIN remediation_proposals p ON p.incident_id = i.id
        LEFT JOIN remediation_logs l ON l.incident_id = i.id
        ORDER BY i.id DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_chat_message(role: str, content: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute('''
        INSERT INTO chat_history (role, content, timestamp)
        VALUES (?, ?, ?)
    ''', (role, content, now))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def get_chat_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history ORDER BY id ASC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ==========================================
# ESTADÍSTICAS GLOBALES DEL SISTEMA (SLA)
# ==========================================

def get_system_stats() -> Dict[str, Any]:
    """
    Calcula métricas agregadas del sistema para el panel SLA:
    - Total de incidentes (abiertos, resueltos)
    - SLA uptime estimado basado en incidentes resueltos vs. tiempo transcurrido
    - Promedio de latencia por servicio
    - Total de remediaciones ejecutadas
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Conteo de incidentes
    cursor.execute("SELECT COUNT(*) FROM incidents")
    total_incidents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'OPEN'")
    open_incidents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'RESOLVED'")
    resolved_incidents = cursor.fetchone()[0]

    # Remediaciones exitosas
    cursor.execute("SELECT COUNT(*) FROM remediation_logs WHERE result = 'SUCCESS'")
    successful_remediations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM remediation_logs")
    total_remediations = cursor.fetchone()[0]

    # Propuestas pendientes
    cursor.execute("SELECT COUNT(*) FROM remediation_proposals WHERE status = 'PENDING_APPROVAL'")
    pending_proposals = cursor.fetchone()[0]

    # Latencia promedio por servicio (últimas 50 métricas)
    cursor.execute("""
        SELECT service_name,
               ROUND(AVG(latency_ms), 2) as avg_latency,
               ROUND(MAX(latency_ms), 2) as max_latency,
               ROUND(MIN(latency_ms), 2) as min_latency,
               SUM(is_error) as error_count,
               COUNT(*) as sample_count
        FROM health_metrics
        GROUP BY service_name
    """)
    latency_rows = cursor.fetchall()
    latency_by_service = {}
    for row in latency_rows:
        r = dict(row)
        service = r.pop("service_name")
        error_rate = r["error_count"] / max(r["sample_count"], 1)
        r["error_rate_pct"] = round(error_rate * 100, 2)
        latency_by_service[service] = r

    # Estimación de SLA uptime (basado en la proporción de checks exitosos)
    cursor.execute("SELECT COUNT(*) FROM health_metrics WHERE is_error = 0")
    healthy_checks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM health_metrics")
    total_checks = cursor.fetchone()[0]

    sla_uptime_pct = round((healthy_checks / max(total_checks, 1)) * 100, 4)

    # Incidente más reciente
    cursor.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT 1")
    last_incident_row = cursor.fetchone()
    last_incident = dict(last_incident_row) if last_incident_row else None

    conn.close()

    return {
        "incidents": {
            "total": total_incidents,
            "open": open_incidents,
            "resolved": resolved_incidents,
            "resolution_rate_pct": round((resolved_incidents / max(total_incidents, 1)) * 100, 1)
        },
        "remediations": {
            "total": total_remediations,
            "successful": successful_remediations,
            "success_rate_pct": round((successful_remediations / max(total_remediations, 1)) * 100, 1),
            "pending_proposals": pending_proposals
        },
        "sla": {
            "uptime_pct": sla_uptime_pct,
            "total_health_checks": total_checks,
            "healthy_checks": healthy_checks
        },
        "latency": latency_by_service,
        "last_incident": last_incident
    }


def cleanup_stale_proposals(older_than_hours: int = 24) -> int:
    """
    Archiva propuestas PENDING_APPROVAL más antiguas que `older_than_hours` horas.
    Las marca como ARCHIVED para no contaminar el dashboard, pero se conservan en DB.
    Retorna la cantidad de propuestas archivadas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    cursor.execute(
        "SELECT id, created_at FROM remediation_proposals WHERE status = 'PENDING_APPROVAL'"
    )
    rows = cursor.fetchall()
    archived_count = 0

    for row in rows:
        try:
            created_str = row["created_at"]
            # Parsear ISO timestamp (con o sin zona horaria)
            created_str_clean = created_str.replace("Z", "+00:00")
            from datetime import timezone as tz
            created_dt = datetime.fromisoformat(created_str_clean)
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)

            age_hours = (now - created_dt).total_seconds() / 3600
            if age_hours >= older_than_hours:
                cursor.execute(
                    "UPDATE remediation_proposals SET status = 'ARCHIVED', decision_notes = ? WHERE id = ?",
                    (f"Auto-archivada por antigüedad ({age_hours:.1f}h > {older_than_hours}h límite).", row["id"])
                )
                archived_count += 1
        except Exception:
            continue

    conn.commit()
    conn.close()
    return archived_count


# ==========================================
# GESTIÓN DE CÓDIGOS OTP POR CORREO
# ==========================================

def store_email_otp(email: str, code: str, expires_at: str) -> int:
    """
    Invalida códigos previos no usados del email e inserta uno nuevo.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    target_email = email.strip().lower()
    cursor.execute("UPDATE email_otp_codes SET used = 1 WHERE LOWER(email) = ? AND used = 0", (target_email,))
    cursor.execute(
        "INSERT INTO email_otp_codes (email, code, expires_at, used, created_at) VALUES (?, ?, ?, 0, ?)",
        (target_email, code, expires_at, datetime.now(timezone.utc).isoformat())
    )
    otp_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return otp_id


def get_valid_email_otp(email: str, code: str) -> Optional[Dict[str, Any]]:
    """
    Busca un código OTP activo (no usado y no expirado) para el correo.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    target_email = email.strip().lower()
    cursor.execute(
        "SELECT * FROM email_otp_codes WHERE LOWER(email) = ? AND code = ? AND used = 0 ORDER BY id DESC LIMIT 1",
        (target_email, code.strip())
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    record = dict(row)
    expires_str = record["expires_at"].replace("Z", "+00:00")
    try:
        expires_dt = datetime.fromisoformat(expires_str)
        if expires_dt.tzinfo is None:
            expires_dt = expires_dt.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_dt:
            return None
    except Exception:
        return None

    return record


def mark_email_otp_used(otp_id: int):
    """
    Marca un código OTP como utilizado.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE email_otp_codes SET used = 1 WHERE id = ?", (otp_id,))
    conn.commit()
    conn.close()

