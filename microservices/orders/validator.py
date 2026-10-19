"""
==============================================================================
DEVPILOT MICROSERVICES - ORDERS SERVICE: COMPONENTE VALIDADOR
Archivo: validator.py
Propósito: Script formal de validación de datos, tipos y reglas de negocio
           (Demostración de componente "Validador" requerido por el docente)
==============================================================================
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


# ----------------------------------------------------------------------------
# 1. ESQUEMAS DE VALIDACIÓN DE ENTRADA (PYDANTIC V2)
# ----------------------------------------------------------------------------

class OrderItemSchema(BaseModel):
    """Validador de ítems individuales de una orden de compra."""
    productId: int = Field(..., gt=0, description="ID único del producto en catálogo (debe ser entero > 0)")
    productName: str = Field(..., min_length=2, max_length=120, description="Nombre legible del producto")
    quantity: int = Field(..., gt=0, le=1000, description="Cantidad requerida (1 - 1000 unidades)")
    unitPrice: float = Field(..., gt=0.0, description="Precio unitario en USD (debe ser positivo)")

    @field_validator("productName")
    @classmethod
    def sanitize_product_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("El nombre del producto no puede estar vacío ni contener solo espacios.")
        return clean


class CreateOrderSchema(BaseModel):
    """Validador para la creación de órdenes de compra con reglas de negocio."""
    userId: int = Field(..., gt=0, description="ID del usuario autenticado que emite la orden")
    items: List[OrderItemSchema] = Field(..., min_length=1, description="Lista de ítems (mínimo 1 ítem obligatorio)")

    @model_validator(mode="after")
    def validate_business_rules(self) -> "CreateOrderSchema":
        """Regla de negocio: no se permiten productos duplicados en la misma orden."""
        product_ids = [item.productId for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("La orden contiene ítems con productId duplicados. Agrupe las cantidades.")
        return self


class DelayRequestSchema(BaseModel):
    """Validador de inyección de latencia para Chaos Testing."""
    delayMs: int = Field(..., ge=0, le=60000, description="Retraso inducido en milisegundos (0 - 60000 ms)")


class ErrorRequestSchema(BaseModel):
    """Validador de inyección de errores HTTP 500 probabilísticos."""
    errorRate: float = Field(..., ge=0.0, le=1.0, description="Tasa probabilística de error (0.0 a 1.0)")


class CrashRequestSchema(BaseModel):
    """Validador de inyección de caída de servicio."""
    hardKill: bool = Field(False, description="Si es True simula terminación violenta del proceso")
    reason: Optional[str] = Field("Simulated cascading failure / thread starvation", max_length=200)


# ----------------------------------------------------------------------------
# 2. FUNCIONES DE VALIDACIÓN PROGRAMÁTICA (VALIDADOR STANDALONE)
# ----------------------------------------------------------------------------

def validate_create_order_payload(payload: Dict[str, Any]) -> CreateOrderSchema:
    """
    Función validadora que parsea y aplica las reglas de negocio sobre un diccionario crudo.
    Lanza ValueError o ValidationError si los datos violan las restricciones.
    """
    if not isinstance(payload, dict):
        raise ValueError("El payload de la orden debe ser un objeto JSON válido.")
    return CreateOrderSchema(**payload)


def validate_chaos_delay_payload(payload: Dict[str, Any]) -> DelayRequestSchema:
    """Valida los parámetros de inyección de retardo."""
    return DelayRequestSchema(**payload)


def validate_chaos_error_payload(payload: Dict[str, Any]) -> ErrorRequestSchema:
    """Valida los parámetros de inyección de tasa de error."""
    return ErrorRequestSchema(**payload)


# ----------------------------------------------------------------------------
# 3. VERIFICADOR AUTÓNOMO DEL VALIDADOR (EJECUCIÓN DIRECTA)
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print(">> [VALIDADOR ORDERS] Ejecutando autoverificación de reglas de validación...")
    
    # Caso Válido
    sample_valid = {
        "userId": 1,
        "items": [
            {"productId": 101, "productName": "Kubernetes Node", "quantity": 2, "unitPrice": 149.99}
        ]
    }
    validated = validate_create_order_payload(sample_valid)
    print(f"  [OK] Payload válido aceptado correctamente: User {validated.userId}, Ítems: {len(validated.items)}")

    # Caso Inválido: Cantidad <= 0
    try:
        sample_invalid = {
            "userId": 1,
            "items": [{"productId": 101, "productName": "Nodo", "quantity": -5, "unitPrice": 10.0}]
        }
        validate_create_order_payload(sample_invalid)
        print("  [FAIL] Debería haber rechazado cantidad negativa.")
    except Exception as e:
        print(f"  [PASS] Rechazado con éxito dato inválido: {e.__class__.__name__}")

    print(">> [VALIDADOR ORDERS] Todos los esquemas y validadores operativos.")
