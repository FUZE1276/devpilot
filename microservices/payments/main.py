import asyncio
import os
import random
import time
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="DevPilot Payments Service",
    description="Microservicio de procesamiento de pagos y transacciones con soporte de Chaos Testing",
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

# Estado de fallos para Chaos Testing (DevPilot Engine)
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

# Middleware de simulación de fallos no invasivo
@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    # Excluir rutas de configuración de fallos para permitir reset en caliente
    if request.url.path.startswith("/fault"):
        return await call_next(request)

    # 1. Simulación de Caída (Crash / 503)
    if fault_state.is_crashed:
        return Response(
            content='{"error": "Service Unavailable", "details": "' + (fault_state.crash_reason or "Simulated payment gateway timeout") + '", "service": "payments"}',
            status_code=503,
            media_type="application/json"
        )

    # 2. Simulación de Retraso / Latencia RTT
    if fault_state.delay_ms > 0:
        await asyncio.sleep(fault_state.delay_ms / 1000.0)

    # 3. Simulación de Error 500 probabilístico
    if fault_state.error_rate > 0 and random.random() < fault_state.error_rate:
        return Response(
            content='{"error": "Internal Server Error", "details": "Payment processor transaction rejection (Simulated Chaos)", "service": "payments"}',
            status_code=500,
            media_type="application/json"
        )

    return await call_next(request)

# ==========================================
# 1. CONTRATO DE SALUD PARA DEVPILOT SRE
# ==========================================
@app.get("/health")
async def health_check():
    uptime = int(time.time() - START_TIME)
    status_str = "DOWN" if fault_state.is_crashed else "UP"
    return {
        "status": status_str,
        "service": "payments",
        "version": "1.0.0",
        "uptimeSeconds": uptime,
        "faultStatus": {
            "delayMs": fault_state.delay_ms,
            "errorRate": fault_state.error_rate,
            "isCrashed": fault_state.is_crashed
        }
    }

# ==========================================
# 2. ENDPOINTS DE INYECCIÓN DE CAOS (CHAOS STUDIO)
# ==========================================
class DelayRequest(BaseModel):
    delayMs: int = Field(..., ge=0, description="Retraso en milisegundos")

class ErrorRequest(BaseModel):
    errorRate: float = Field(..., ge=0.0, le=1.0, description="Tasa de error entre 0.0 y 1.0")

class CrashRequest(BaseModel):
    reason: Optional[str] = Field("Simulated payment processor connection failure", description="Motivo del fallo")

@app.post("/fault/delay")
async def inject_delay(payload: DelayRequest):
    fault_state.delay_ms = payload.delayMs
    return {"success": True, "message": f"Delay set to {payload.delayMs}ms", "faults": fault_state.to_dict()}

@app.post("/fault/error")
async def inject_error(payload: ErrorRequest):
    fault_state.error_rate = payload.errorRate
    return {"success": True, "message": f"Error rate set to {int(payload.errorRate * 100)}%", "faults": fault_state.to_dict()}

@app.post("/fault/crash")
async def inject_crash(payload: CrashRequest):
    fault_state.is_crashed = True
    fault_state.crash_reason = payload.reason
    return {"success": True, "message": "Service simulated crash active (HTTP 503)", "faults": fault_state.to_dict()}

@app.post("/fault/reset")
async def reset_faults():
    fault_state.reset()
    return {"success": True, "message": "All faults cleared, payments service back to nominal state", "faults": fault_state.to_dict()}

# ==========================================
# 3. ENDPOINTS DE NEGOCIO (TRANSACCIONES DE PAGO)
# ==========================================
class PaymentTransaction(BaseModel):
    id: str
    orderId: str
    customer: str
    amount: float
    currency: str = "USD"
    paymentMethod: str
    status: str
    createdAt: str

PAYMENTS_DB: List[PaymentTransaction] = [
    PaymentTransaction(
        id="PAY-2026-001",
        orderId="ORD-2026-001",
        customer="Juan Perez",
        amount=149.99,
        currency="USD",
        paymentMethod="Credit Card (Visa)",
        status="COMPLETED",
        createdAt="2026-09-01T18:30:00Z"
    ),
    PaymentTransaction(
        id="PAY-2026-002",
        orderId="ORD-2026-002",
        customer="Maria Gomez",
        amount=289.50,
        currency="USD",
        paymentMethod="PayPal Express",
        status="COMPLETED",
        createdAt="2026-09-01T19:15:00Z"
    ),
    PaymentTransaction(
        id="PAY-2026-003",
        orderId="ORD-2026-003",
        customer="Carlos Mendoza",
        amount=45.00,
        currency="USD",
        paymentMethod="Apple Pay",
        status="PROCESSING",
        createdAt="2026-09-01T20:45:00Z"
    )
]

@app.get("/payments")
async def list_payments():
    return {
        "success": True,
        "count": len(PAYMENTS_DB),
        "data": [p.dict() for p in PAYMENTS_DB]
    }

@app.get("/")
async def root():
    return {
        "service": "DevPilot Payments Service",
        "status": "OPERATIONAL",
        "docs": "/docs",
        "health": "/health"
    }
