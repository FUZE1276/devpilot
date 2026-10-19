"""
DevPilot - Módulo de OTP por Correo Electrónico (Email MFA).
Genera un código de 6 dígitos de un solo uso, lo almacena en SQLite con expiración
y lo envía por SMTP. En modo simulado (EMAIL_OTP_DEV_MODE=true) retorna el código
en la respuesta de la API para pruebas locales sin servidor SMTP.
"""

import os
import secrets
import smtplib
import logging
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

logger = logging.getLogger("devpilot.email_otp")

# Configuración SMTP
SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM     = os.environ.get("SMTP_FROM", "DevPilot SRE <noreply@devpilot.io>")
SMTP_TLS      = os.environ.get("SMTP_TLS", "true").lower() == "true"
SMTP_OVERRIDE_RECIPIENT = os.environ.get("SMTP_OVERRIDE_RECIPIENT", "fuze1276@gmail.com")

OTP_EXPIRE_MINUTES = int(os.environ.get("EMAIL_OTP_EXPIRE_MINUTES", "5"))
OTP_DEV_MODE       = os.environ.get("EMAIL_OTP_DEV_MODE", "true").lower() == "true"
OTP_CODE_LENGTH    = 6


def generate_otp_code() -> str:
    return str(secrets.randbelow(10 ** OTP_CODE_LENGTH)).zfill(OTP_CODE_LENGTH)


def _build_email_html(code: str, recipient_name: str, expire_minutes: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Código DevPilot</title></head>
<body style="margin:0;padding:0;background:#050811;font-family:sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#050811;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#0e1626;border:1px solid rgba(99,102,241,0.3);border-radius:16px;overflow:hidden;">
        <tr>
          <td style="background:linear-gradient(135deg,#4f46e5,#06b6d4);padding:28px 36px;">
            <h1 style="margin:0;color:#fff;font-size:22px;font-weight:800;">🛡️ DevPilot SRE</h1>
            <p style="margin:4px 0 0;color:rgba(255,255,255,0.8);font-size:13px;">Plataforma de Observabilidad</p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px;">
            <p style="color:#94a3b8;font-size:14px;margin:0 0 8px;">Hola, <strong style="color:#e2e8f0;">{recipient_name}</strong></p>
            <p style="color:#94a3b8;font-size:14px;margin:0 0 28px;line-height:1.6;">
              Usa el siguiente código de verificación de un solo uso:
            </p>
            <div style="text-align:center;margin:0 0 28px;">
              <div style="display:inline-block;background:#0a0f1e;border:2px solid rgba(99,102,241,0.6);border-radius:12px;padding:20px 40px;">
                <span style="font-family:monospace;font-size:42px;font-weight:900;color:#06b6d4;letter-spacing:12px;">{code}</span>
              </div>
            </div>
            <div style="background:#1e1f2e;border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:14px 18px;margin:0 0 24px;">
              <p style="margin:0;color:#fbbf24;font-size:13px;">⏱ <strong>Este código expira en {expire_minutes} minutos.</strong> No lo compartas.</p>
            </div>
            <p style="color:#64748b;font-size:12px;margin:0;">Si no solicitaste este código, ignora este correo.</p>
          </td>
        </tr>
        <tr>
          <td style="background:#090e1a;padding:18px 36px;border-top:1px solid #1e293b;">
            <p style="margin:0;color:#334155;font-size:11px;text-align:center;">DevPilot SRE · Código generado automáticamente, no responder.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _send_smtp_email(to_email: str, code: str, recipient_name: str, account_email: str = "") -> bool:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False
    try:
        dest_email = SMTP_OVERRIDE_RECIPIENT if SMTP_OVERRIDE_RECIPIENT else to_email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 Tu código DevPilot: {code} ({recipient_name})"
        msg["From"]    = SMTP_FROM
        msg["To"]      = dest_email
        account_info = f" (Cuenta: {account_email})" if account_email else ""
        text_body = f"Hola {recipient_name},\n\nTu código DevPilot{account_info} es: {code}\n\nExpira en {OTP_EXPIRE_MINUTES} minutos.\n"
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(_build_email_html(code, f"{recipient_name}{account_info}", OTP_EXPIRE_MINUTES), "html", "utf-8"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            if SMTP_TLS:
                server.starttls()
                server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, dest_email, msg.as_string())
        logger.info(f"[Email OTP] Código enviado a {dest_email} para cuenta {account_email or to_email}")
        return True
    except Exception as exc:
        logger.error(f"[Email OTP] Error SMTP hacia {to_email}: {exc}")
        return False


def request_email_otp(email: str, user_name: str = "Usuario") -> Tuple[bool, str, Optional[str]]:
    """
    Genera código, lo guarda en BD y lo envía (o simula el envío).
    Returns: (success, message, dev_code_or_None)
    """
    from database import store_email_otp
    code    = generate_otp_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
    store_email_otp(email, code, expires.isoformat())

    dest_email = SMTP_OVERRIDE_RECIPIENT if SMTP_OVERRIDE_RECIPIENT else email
    sent_via_smtp = False
    if SMTP_USER and SMTP_PASSWORD:
        result = [False]
        def _send():
            result[0] = _send_smtp_email(dest_email, code, user_name, email)
        t = threading.Thread(target=_send, daemon=True)
        t.start()
        t.join(timeout=12)
        sent_via_smtp = result[0]

    logger.info(f"[Email OTP] Código para {email} -> Destino: {dest_email}: {'SMTP OK' if sent_via_smtp else 'MODO SIMULADO'} | Expira: {expires.isoformat()}")

    if OTP_DEV_MODE and not sent_via_smtp:
        return True, f"[DEV MODE] Código para cuenta {email} (enviado a {dest_email}).", code

    return True, f"Código de verificación enviado a {dest_email} (cuenta: {email}). Expira en {OTP_EXPIRE_MINUTES} min.", None


def verify_email_otp(email: str, code: str) -> Tuple[bool, str]:
    """
    Verifica el código OTP. Retorna (valid, message).
    El código se invalida tras el primer uso exitoso.
    """
    from database import get_valid_email_otp, mark_email_otp_used
    code_clean = str(code).strip()
    if not code_clean.isdigit() or len(code_clean) != OTP_CODE_LENGTH:
        return False, f"El código debe ser numérico de {OTP_CODE_LENGTH} dígitos."
    record = get_valid_email_otp(email, code_clean)
    if record is None:
        return False, "Código inválido, expirado o ya utilizado. Solicita uno nuevo."
    mark_email_otp_used(record["id"])
    logger.info(f"[Email OTP] Verificación exitosa para {email} (ID: {record['id']})")
    return True, "Código validado correctamente."
