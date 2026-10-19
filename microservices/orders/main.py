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
    title="DevPilot Orders Service",
    description="Microservicio de gestión de órdenes de compra con capacidades de Chaos Testing",
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

# Modelos
class DelayRequest(BaseModel):
    delayMs: int = Field(..., ge=0)

class ErrorRequest(BaseModel):
    errorRate: float = Field(..., ge=0.0, le=1.0)

class CrashRequest(BaseModel):
    hardKill: bool = Field(False)
    reason: Optional[str] = Field("Simulated cascading failure / thread starvation")

class OrderItem(BaseModel):
    productId: int
    productName: str
    quantity: int
    unitPrice: float

class CreateOrderRequest(BaseModel):
    userId: int
    items: List[OrderItem]

class Order(BaseModel):
    id: str
    userId: int
    items: List[OrderItem]
    totalAmount: float
    status: str
    createdAt: str

# Base de datos simulada de órdenes
ORDERS_DB: List[Dict[str, Any]] = [
    {
        "id": "ORD-9021",
        "userId": 1,
        "items": [{"productId": 101, "productName": "Kubernetes Pro Node", "quantity": 2, "unitPrice": 149.99}],
        "totalAmount": 299.98,
        "status": "COMPLETED",
        "createdAt": "2026-08-25T14:10:00Z"
    },
    {
        "id": "ORD-9022",
        "userId": 2,
        "items": [
            {"productId": 102, "productName": "High IOPS SSD Storage 1TB", "quantity": 4, "unitPrice": 89.50},
            {"productId": 105, "productName": "DevPilot Telemetry Agent", "quantity": 1, "unitPrice": 29.99}
        ],
        "totalAmount": 387.99,
        "status": "PROCESSING",
        "createdAt": "2026-08-25T16:25:00Z"
    }
]

# Middleware para simulación de fallos
@app.middleware("http")
async def fault_injection_middleware(request: Request, call_next):
    if request.url.path.startswith("/fault"):
        return await call_next(request)

    # 1. Crash
    if fault_state.is_crashed:
        return Response(
            content='{"error": "Service Unavailable", "details": "' + (fault_state.crash_reason or "Service crashed") + '", "service": "orders"}',
            status_code=503,
            media_type="application/json"
        )

    # 2. Retraso
    if fault_state.delay_ms > 0:
        await asyncio.sleep(fault_state.delay_ms / 1000.0)

    # 3. Error 500
    if fault_state.error_rate > 0:
        if random.random() < fault_state.error_rate:
            return Response(
                content='{"error": "Internal Server Error", "details": "Simulated chaos error in Orders Service", "service": "orders"}',
                status_code=500,
                media_type="application/json"
            )

    return await call_next(request)

# ==========================================
# ENDPOINTS DE NEGOCIO Y SALUD
# ==========================================

@app.get("/health")
async def health_check():
    uptime = int(time.time() - START_TIME)
    return {
        "status": "UP",
        "service": "orders",
        "version": "1.0.0",
        "uptimeSeconds": uptime,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "faultStatus": fault_state.to_dict()
    }

@app.get("/orders")
async def list_orders(userId: Optional[int] = None):
    if userId is not None:
        filtered = [o for o in ORDERS_DB if o["userId"] == userId]
        return {"success": True, "count": len(filtered), "data": filtered}
    return {"success": True, "count": len(ORDERS_DB), "data": ORDERS_DB}

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    for o in ORDERS_DB:
        if o["id"] == order_id:
            return {"success": True, "data": o}
    raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

@app.post("/orders", status_code=201)
async def create_order(payload: CreateOrderRequest):
    total = sum(item.quantity * item.unitPrice for item in payload.items)
    new_order = {
        "id": f"ORD-{random.randint(1000, 9999)}",
        "userId": payload.userId,
        "items": [item.dict() for item in payload.items],
        "totalAmount": round(total, 2),
        "status": "PENDING",
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    ORDERS_DB.append(new_order)
    return {"success": True, "message": "Order created successfully", "data": new_order}

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
        "message": f"Fallo '{type}' configurado correctamente en Orders Service",
        "faultState": fault_state.to_dict()
    }

@app.post("/fault/reset")
async def reset_faults():
    fault_state.reset()
    return {
        "message": "All faults cleared. Orders service is healthy.",
        "faultState": fault_state.to_dict()
    }

@app.get("/fault/status")
async def get_fault_status():
    return fault_state.to_dict()

# ==========================================
# ENDPOINTS CRUD EXTENDIDOS
# ==========================================

VALID_STATUSES = ["PENDING", "PROCESSING", "SHIPPED", "COMPLETED", "CANCELLED"]

class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., description=f"Nuevo estado: {', '.join(VALID_STATUSES)}")
    note: Optional[str] = Field(None, description="Nota opcional sobre el cambio de estado")

@app.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, payload: UpdateOrderStatusRequest):
    """Actualiza el estado de una orden en el flujo de cumplimiento."""
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido '{payload.status}'. Válidos: {VALID_STATUSES}"
        )
    for order in ORDERS_DB:
        if order["id"] == order_id:
            old_status = order["status"]
            order["status"] = payload.status
            order["updatedAt"] = datetime.now(timezone.utc).isoformat()
            if payload.note:
                order["statusNote"] = payload.note
            return {
                "success": True,
                "message": f"Orden {order_id} actualizada: {old_status} → {payload.status}",
                "data": order
            }
    raise HTTPException(status_code=404, detail=f"Orden '{order_id}' no encontrada.")

@app.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancela una orden marcándola como CANCELLED (no la elimina del historial)."""
    for order in ORDERS_DB:
        if order["id"] == order_id:
            if order["status"] == "COMPLETED":
                raise HTTPException(status_code=400, detail="No se puede cancelar una orden ya completada.")
            order["status"] = "CANCELLED"
            order["updatedAt"] = datetime.now(timezone.utc).isoformat()
            return {"success": True, "message": f"Orden {order_id} cancelada.", "data": order}
    raise HTTPException(status_code=404, detail=f"Orden '{order_id}' no encontrada.")

# ==========================================
# ENDPOINT DE MÉTRICAS INTERNAS
# ==========================================

@app.get("/metrics")
async def get_metrics_summary():
    """Estadísticas internas del microservicio para observabilidad."""
    uptime = int(time.time() - START_TIME)
    status_counts: Dict[str, int] = {}
    total_revenue = 0.0
    for order in ORDERS_DB:
        s = order.get("status", "UNKNOWN")
        status_counts[s] = status_counts.get(s, 0) + 1
        if order.get("status") != "CANCELLED":
            total_revenue += order.get("totalAmount", 0)
    return {
        "service": "orders",
        "version": "1.0.0",
        "uptimeSeconds": uptime,
        "uptimeHuman": f"{uptime // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
        "orders": {
            "total": len(ORDERS_DB),
            "byStatus": status_counts,
            "totalRevenue": round(total_revenue, 2)
        },
        "faultStatus": fault_state.to_dict(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ============================================================================
# 3. EJECUCIÓN DIRECTA COMO SOFTWARE NATIVO (SIN CONTENEDOR DOCKER)
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("  >> DEVPILOT ORDERS SERVICE - EJECUCIÓN DIRECTA COMO SOFTWARE PURO")
    print("  >> Host: http://127.0.0.1:3003 | Puerto: 3003")
    print("  >> Validador: validator.py | Endpoints: /health, /orders, /metrics")
    print("=" * 70)
    uvicorn.run("main:app", host="0.0.0.0", port=3003, reload=False)

