"""
DevPilot Build Tests - Suite de Autenticación, Seguridad Criptográfica y RBAC
Valida la generación/verificación de JWT, algoritmo TOTP RFC 6238 y matriz de permisos RBAC.
"""

import sys
import os
import unittest
from fastapi import HTTPException

# Agregar devpilot_core al path de python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "devpilot_core")))

from auth import (
    create_jwt_token,
    verify_jwt_token,
    verify_totp_code,
    generate_current_totp,
    authenticate_user_credentials,
    get_effective_user_permissions,
    ROLE_PERMISSIONS,
    ALL_SYSTEM_PERMISSIONS,
    PRESET_USERS
)


class TestAuthAndSecurity(unittest.TestCase):

    def test_jwt_generation_and_validation(self):
        """Prueba que los tokens JWT se firmen con HMAC-SHA256 y se validen correctamente."""
        payload = {
            "sub": "test@devpilot.io",
            "name": "Test User",
            "role": "Administrador"
        }
        token = create_jwt_token(payload, expires_in=60)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token.split(".")), 2)

        # Validación exitosa
        decoded = verify_jwt_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "test@devpilot.io")
        self.assertEqual(decoded["role"], "Administrador")

    def test_jwt_tampering_detection(self):
        """Prueba que cualquier alteración en el token JWT levante HTTPException 401."""
        payload = {"sub": "admin@devpilot.io", "role": "Cliente"}
        token = create_jwt_token(payload, expires_in=60)
        
        # Modificar el cuerpo del token para simular ataque Man-in-the-Middle
        parts = token.split(".")
        tampered_token = f"{parts[0]}.eyJyYW5kb20iOiAxfQ.{parts[2]}"
        
        with self.assertRaises(HTTPException) as cm:
            verify_jwt_token(tampered_token)
        self.assertEqual(cm.exception.status_code, 401)

    def test_jwt_expiration(self):
        """Prueba que un token con tiempo expirado sea rechazado con HTTPException 401."""
        payload = {"sub": "expired@devpilot.io"}
        token = create_jwt_token(payload, expires_in=-10)  # Expirado en el pasado
        
        with self.assertRaises(HTTPException) as cm:
            verify_jwt_token(token)
        self.assertEqual(cm.exception.status_code, 401)

    def test_totp_generation_and_verification(self):
        """Prueba el algoritmo TOTP RFC 6238 de 6 dígitos numéricos."""
        secret = "JBSWY3DPEHPK3PXP"
        code = generate_current_totp(secret)
        
        self.assertIsInstance(code, str)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

        # Validar el código actual
        is_valid = verify_totp_code(code, secret)
        self.assertTrue(is_valid)

        # Rechazar código inválido
        is_invalid = verify_totp_code("000000" if code != "000000" else "111111", secret)
        self.assertFalse(is_invalid)

    def test_rbac_roles_hierarchy(self):
        """Valida que la matriz RBAC contemple los roles y permisos de la arquitectura IEEE 830."""
        self.assertIn("Super_Administrador", ROLE_PERMISSIONS)
        self.assertIn("Administrador", ROLE_PERMISSIONS)
        self.assertIn("Cliente", ROLE_PERMISSIONS)

        # Super_Administrador debe poseer permisos de gestión de usuarios y configuración de sistema
        super_perms = ROLE_PERMISSIONS["Super_Administrador"]
        self.assertIn("users:manage", super_perms)
        self.assertIn("system:config", super_perms)
        self.assertIn("chaos:inject", super_perms)
        self.assertIn("remediation:execute", super_perms)

        # Cliente solo debe tener permisos de solo lectura de métricas
        client_perms = ROLE_PERMISSIONS["Cliente"]
        self.assertIn("metrics:read", client_perms)
        self.assertNotIn("chaos:inject", client_perms)
        self.assertNotIn("remediation:execute", client_perms)

    def test_preset_users_authentication(self):
        """Prueba la autenticación de los usuarios preconfigurados del sistema."""
        # Usuario Super Admin
        super_auth = authenticate_user_credentials("superadmin", "SuperAdmin2026*")
        self.assertIsNotNone(super_auth)
        self.assertEqual(super_auth["role"], "Super_Administrador")

        # Usuario Admin
        admin_auth = authenticate_user_credentials("admin", "AdminPass2026*")
        self.assertIsNotNone(admin_auth)
        self.assertEqual(admin_auth["role"], "Administrador")

        # Credenciales incorrectas
        bad_auth = authenticate_user_credentials("admin", "WrongPassword!")
        self.assertIsNone(bad_auth)


if __name__ == "__main__":
    unittest.main()
