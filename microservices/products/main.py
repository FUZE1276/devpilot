import asyncio
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="DevPilot Products Service",
    description="Microservicio de gestión de productos con simulación de fallas para Chaos Testing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

# Estado de fallos
class FaultState:
    def __init__(self):
        self.delay_ms: int = 0
        self.error_rate: float = 0.0
        self.is_crashed: bool = False
        self.crash_reason: Optional[str] = None

    def reset(self):
        self.delay_ms = 0
        self.error_rate = 0.0
        self.is_crashed = False
        self.crash_reason = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "delay_ms": self.delay_ms,
            "error_rate": self.error_rate,
            "is_crashed": self.is_crashed,
            "crash_reason": self.crash_reason
        }

fault_state = FaultState()

# Modelos Pydantic
class DelayRequest(BaseModel):
    delayMs: int = Field(..., ge=0, description="Retraso en milisegundos")

class ErrorRequest(BaseModel):
    errorRate: float = Field(..., ge=0.0, le=1.0, description="Tasa de error entre 0.0 y 1.0")

class CrashRequest(BaseModel):
    hardKill: bool = Field(False, description="Si es True, cierra el proceso de Python")
    reason: Optional[str] = Field("Simulated memory overflow or deadlock", description="Motivo del fallo")

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    sku: str

# Base de datos simulada
PRODUCTS_DB: List[Product] = [
    Product(id=101, name="Kubernetes Pro Node", category="Compute", price=149.99, stock=45, sku="K8S-NODE-01"),
    Product(id=102, name="High IOPS SSD Storage 1TB", category="Storage", price=89.50, stock=120, sku="SSD-1TB-IO"),
    Product(id=103, name="Enterprise Load Balancer", category="Networking", price=210.00, stock=18, sku="NET-LB-ENT"),
    Product(id=104, name="Managed PostgreSQL Instance", category="Database", price=175.00, stock=32, sku="DB-PG-MGD"),
    Product(id=105, name="DevPilot Telemetry Agent", category="Observability", price=29.99, stock=500, sku="OBS-DVP-01")
]

# Middleware para inyección de fallos
@app.middleware("http")
async def fault_injection_middleware(request: Request, call_next):
    # Excluir rutas de configuración de fallos del middleware para permitir reset
    if request.url.path.startswith("/fault"):
        return await call_next(request)

    # 1. Simulación de Crash
    if fault_state.is_crashed:
        return Response(
            content='{"error": "Service Unavailable", "details": "' + (fault_state.crash_reason or "Service in crashed state") + '", "service": "products"}',
            status_code=503,
            media_type="application/json"
        )

    # 2. Simulación de Latencia
    if fault_state.delay_ms > 0:
        await asyncio.sleep(fault_state.delay_ms / 1000.0)

    # 3. Simulación de Error 500
    if fault_state.error_rate > 0:
        if random.random() < fault_state.error_rate:
            return Response(
                content='{"error": "Internal Server Error", "details": "Simulated chaos error in Products Service", "service": "products"}',
                status_code=500,
                media_type="application/json"
            )

    return await call_next(request)

# ==========================================
# ENDPOINTS DE SALUD Y NEGOCIO
# ==========================================

@app.get("/health")
async def health_check():
    uptime = int(time.time() - START_TIME)
    return {
        "status": "UP",
        "service": "products",
        "version": "1.0.0",
        "uptimeSeconds": uptime,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "faultStatus": fault_state.to_dict()
    }

@app.get("/products")
async def list_products(category: Optional[str] = None):
    if category:
        filtered = [p for p in PRODUCTS_DB if p.category.lower() == category.lower()]
        return {"success": True, "count": len(filtered), "data": filtered}
    return {"success": True, "count": len(PRODUCTS_DB), "data": PRODUCTS_DB}

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    for p in PRODUCTS_DB:
        if p.id == product_id:
            return {"success": True, "data": p}
    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

# ==========================================
# ENDPOINTS DE INYECCIÓN DE FALLOS (CHAOS)
# ==========================================

@app.post("/fault/delay")
async def inject_delay(payload: DelayRequest):
    fault_state.delay_ms = payload.delayMs
    return {
        "message": f"Delay fault configured to {payload.delayMs}ms",
        "faultState": fault_state.to_dict()
    }

@app.post("/fault/error")
async def inject_error(payload: ErrorRequest):
    fault_state.error_rate = payload.errorRate
    return {
        "message": f"Error rate configured to {int(payload.errorRate * 100)}%",
        "faultState": fault_state.to_dict()
    }

@app.post("/fault/crash")
async def inject_crash(payload: CrashRequest):
    if payload.hardKill:
        # Cerrar el proceso asíncronamente
        loop = asyncio.get_event_loop()
        loop.call_later(0.2, lambda: sys.exit(1))
        return {"message": "Service process terminating immediately (hard kill)..."}
    
    fault_state.is_crashed = True
    fault_state.crash_reason = payload.reason
    return {
        "message": "Service marked as CRASHED (returning 503)",
        "faultState": fault_state.to_dict()
    }

@app.api_route("/simular-fallo", methods=["GET", "POST"])
async def simular_fallo(type: Optional[str] = "delay"):
    if type == "delay":
        fault_state.delay_ms = 2500
    elif type == "error":
        fault_state.error_rate = 0.5
    elif type == "crash":
        fault_state.is_crashed = True
        fault_state.crash_reason = "Fallo simulado vía /simular-fallo"
    elif type == "reset":
        fault_state.reset()
    return {
        "message": f"Fallo '{type}' configurado correctamente en Products Service",
        "faultState": fault_state.to_dict()
    }

@app.post("/fault/reset")
async def reset_faults():
    fault_state.reset()
    return {
        "message": "All faults cleared. Products service is healthy.",
        "faultState": fault_state.to_dict()
    }

@app.get("/fault/status")
async def get_fault_status():
    return fault_state.to_dict()

# ==========================================
# ENDPOINTS CRUD EXTENDIDOS
# ==========================================

@app.patch("/products/{product_id}/stock")
async def update_product_stock(product_id: int, stock: int = 0):
    """Actualiza el stock disponible de un producto."""
    if stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo.")
    for p in PRODUCTS_DB:
        if p.id == product_id:
            p.stock = stock
            return {"success": True, "message": f"Stock del producto {product_id} actualizado a {stock}.", "data": p}
    raise HTTPException(status_code=404, detail=f"Producto con ID {product_id} no encontrado.")

@app.delete("/products/{product_id}", status_code=200)
async def delete_product(product_id: int):
    """Elimina un producto del catálogo simulado."""
    global PRODUCTS_DB
    original_len = len(PRODUCTS_DB)
    PRODUCTS_DB = [p for p in PRODUCTS_DB if p.id != product_id]
    if len(PRODUCTS_DB) == original_len:
        raise HTTPException(status_code=404, detail=f"Producto con ID {product_id} no encontrado.")
    return {"success": True, "message": f"Producto {product_id} eliminado del catálogo."}

# ==========================================
# ENDPOINT DE MÉTRICAS INTERNAS
# ==========================================

_request_counter = {"total": 0, "errors": 0}

@app.get("/metrics")
async def get_metrics_summary():
    """Estadísticas internas del microservicio para observabilidad."""
    uptime = int(time.time() - START_TIME)
    categories = list({p.category for p in PRODUCTS_DB})
    return {
        "service": "products",
        "version": "1.0.0",
        "uptimeSeconds": uptime,
        "uptimeHuman": f"{uptime // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
        "catalog": {
            "totalProducts": len(PRODUCTS_DB),
            "categories": categories,
            "totalStock": sum(p.stock for p in PRODUCTS_DB),
            "avgPrice": round(sum(p.price for p in PRODUCTS_DB) / max(len(PRODUCTS_DB), 1), 2)
        },
        "faultStatus": fault_state.to_dict(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
