"""
DevPilot Build Tests - Suite de Persistencia Relacional y Base de Datos SQLite
Valida la inicialización de esquemas, CRUD de microservicios, umbrales SLA, auditoría e incidentes.
"""

import sys
import os
import unittest
import tempfile

# Usar base de datos aislada temporal para pruebas
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp_db_path = temp_db.name
temp_db.close()
os.environ["DB_PATH"] = temp_db_path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "devpilot_core")))

import database


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        database.DB_PATH = temp_db_path
        database.init_db()

    @classmethod
    def tearDownClass(cls):
        try:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
        except Exception:
            pass

    def test_schema_initialization(self):
        """Verifica que las tablas nucleares del sistema se creen correctamente."""
        services = database.get_services()
        self.assertIsInstance(services, list)
        self.assertGreaterEqual(len(services), 3)  # users, products, orders sembrados

    def test_custom_service_lifecycle(self):
        """Prueba la creación, lectura, actualización de umbrales SLA y eliminación de un servicio."""
        # 1. Crear servicio
        created = database.create_custom_service(
            name="test_service",
            display_name="Test Microservice",
            service_type="Python",
            url="http://test_service:8080",
            container_name="devpilot_test",
            latency_threshold_ms=1500.0,
            error_threshold_pct=0.15
        )
        self.assertTrue(created)

        # 2. Consultar servicio
        svc = database.get_service("test_service")
        self.assertIsNotNone(svc)
        self.assertEqual(svc["display_name"], "Test Microservice")
        self.assertEqual(svc["latency_threshold_ms"], 1500.0)

        # 3. Actualizar umbrales SLA
        updated = database.update_service_thresholds("test_service", 2500.0, 0.30)
        self.assertTrue(updated)
        svc_updated = database.get_service("test_service")
        self.assertEqual(svc_updated["latency_threshold_ms"], 2500.0)

        # 4. Eliminar servicio
        deleted = database.delete_custom_service("test_service")
        self.assertTrue(deleted)
        self.assertIsNone(database.get_service("test_service"))

    def test_audit_trail_logging(self):
        """Prueba que los eventos de remediación y auditoría forense persistan correctamente."""
        inc_id = database.create_incident(
            service_name="products",
            title="High Latency Warning",
            description="Latency exceeded threshold",
            incident_type="LATENCY_HIGH",
            severity="HIGH"
        )
        database.log_remediation(
            incident_id=inc_id,
            service_name="products",
            action_type="RESTART_CONTAINER",
            result="SUCCESS",
            details="Test automated recovery audit log",
            operator_user="admin@devpilot.io"
        )

        audit_history = database.get_audit_trail(limit=10)
        self.assertIsInstance(audit_history, list)
        self.assertGreater(len(audit_history), 0)
        latest = audit_history[0]
        self.assertEqual(latest["service_name"], "products")


if __name__ == "__main__":
    unittest.main()
