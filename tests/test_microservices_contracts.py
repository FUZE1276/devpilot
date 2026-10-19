"""
DevPilot Build Tests - Suite de Contratos de Microservicios (Products, Orders, Payments)
Valida los contratos de observabilidad (/health), inyección de caos y endpoints de negocio.
"""

import sys
import os
import unittest
from starlette.testclient import TestClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "microservices", "products"))
sys.path.insert(0, os.path.join(BASE_DIR, "microservices", "orders"))
sys.path.insert(0, os.path.join(BASE_DIR, "microservices", "payments"))

# Cargar las aplicaciones FastAPI de los microservicios
import importlib.util

def load_app(module_path):
    spec = importlib.util.spec_from_file_location("main", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app

products_app = load_app(os.path.join(BASE_DIR, "microservices", "products", "main.py"))
orders_app = load_app(os.path.join(BASE_DIR, "microservices", "orders", "main.py"))
payments_app = load_app(os.path.join(BASE_DIR, "microservices", "payments", "main.py"))


class TestMicroservicesContracts(unittest.TestCase):

    def setUp(self):
        self.products_client = TestClient(products_app)
        self.orders_client = TestClient(orders_app)
        self.payments_client = TestClient(payments_app)

    def test_products_service_contract(self):
        """Verifica el contrato del microservicio Products (FastAPI)."""
        # 1. Healthcheck
        res = self.products_client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "UP")
        self.assertEqual(data["service"], "products")

        # 2. Catálogo de productos
        res_prod = self.products_client.get("/products")
        self.assertEqual(res_prod.status_code, 200)
        prods = res_prod.json()
        items = prods.get("data", prods)
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0)

        # 3. Inyección y reseteo de fallos
        res_fault = self.products_client.post("/fault/delay", json={"delayMs": 100})
        self.assertEqual(res_fault.status_code, 200)
        res_reset = self.products_client.post("/fault/reset")
        self.assertEqual(res_reset.status_code, 200)

    def test_orders_service_contract(self):
        """Verifica el contrato del microservicio Orders (FastAPI)."""
        # 1. Healthcheck
        res = self.orders_client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "UP")
        self.assertEqual(data["service"], "orders")

        # 2. Listado de órdenes
        res_orders = self.orders_client.get("/orders")
        self.assertEqual(res_orders.status_code, 200)
        orders = res_orders.json()
        items = orders.get("data", orders)
        self.assertIsInstance(items, list)

        # 3. Reset de fallos
        res_reset = self.orders_client.post("/fault/reset")
        self.assertEqual(res_reset.status_code, 200)

    def test_payments_service_contract(self):
        """Verifica el contrato del microservicio Payments (FastAPI)."""
        # 1. Healthcheck
        res = self.payments_client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "UP")
        self.assertEqual(data["service"], "payments")

        # 2. Catálogo de pagos
        res_pay = self.payments_client.get("/payments")
        self.assertEqual(res_pay.status_code, 200)
        pay_data = res_pay.json()
        self.assertTrue(pay_data["success"])
        self.assertIsInstance(pay_data["data"], list)

        # 3. Reset de fallos
        res_reset = self.payments_client.post("/fault/reset")
        self.assertEqual(res_reset.status_code, 200)


if __name__ == "__main__":
    unittest.main()
