import asyncio
import json
import logging
import time
from typing import Dict, Any, List
import httpx

from database import (
    get_services,
    upsert_service_status,
    insert_health_metric,
    get_recent_metrics,
    create_incident,
    get_open_incident_for_service,
    auto_resolve_open_incidents_for_service
)
from docker_manager import get_container_logs
from ai_agent import ai_agent

logger = logging.getLogger("devpilot.monitor")

CHECK_INTERVAL_SECONDS = 5
ROLLING_WINDOW_SIZE = 10

class ServiceMonitor:
    def __init__(self):
        self.is_running = False
        self._task: asyncio.Task = None
        self._client: httpx.AsyncClient = None
        self.consecutive_failures: Dict[str, int] = {}

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
        self._client = httpx.AsyncClient(timeout=3.5, limits=limits)
        logger.info("DevPilot Health Monitor started with persistent HTTP pool (Interval: %ds)", CHECK_INTERVAL_SECONDS)
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._client:
            await self._client.aclose()
        logger.info("DevPilot Health Monitor stopped.")

    async def _monitor_loop(self):
        # Período de gracia inicial de 2 segundos para permitir que los microservicios terminen de levantar
        await asyncio.sleep(2)
        while self.is_running:
            try:
                await self.run_check_cycle()
            except Exception as e:
                logger.error(f"Error in monitor loop cycle: {e}", exc_info=True)
            
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

    async def run_check_cycle(self):
        services = get_services()
        if not self._client or self._client.is_closed:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
            self._client = httpx.AsyncClient(timeout=3.5, limits=limits)
            
        tasks = [self._check_single_service(self._client, s) for s in services]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_single_service(self, client: httpx.AsyncClient, service: Dict[str, Any]):
        service_name = service["name"]
        url = service["url"]
        health_url = f"{url}/health"
        
        latency_threshold = float(service.get("latency_threshold_ms") or 2000.0)
        error_threshold = float(service.get("error_threshold_pct") or 0.20)

        start_t = time.perf_counter()
        status_code = 0
        is_error = False
        uptime_seconds = int(service.get("uptime_seconds") or 0)
        active_faults = "{}"
        error_detail = None

        try:
            response = await client.get(health_url)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            status_code = response.status_code

            if response.status_code == 200:
                self.consecutive_failures[service_name] = 0
                try:
                    data = response.json()
                    uptime_seconds = int(data.get("uptimeSeconds") or 0)
                    fault_status = data.get("faultStatus", {})
                    active_faults = json.dumps(fault_status)
                except Exception:
                    pass
            else:
                is_error = True
                self.consecutive_failures[service_name] = self.consecutive_failures.get(service_name, 0) + 1
                error_detail = f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            status_code = 504
            is_error = True
            self.consecutive_failures[service_name] = self.consecutive_failures.get(service_name, 0) + 1
            error_detail = f"Timeout ({elapsed_ms:.0f}ms)"

        except Exception:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            status_code = 503
            is_error = True
            self.consecutive_failures[service_name] = self.consecutive_failures.get(service_name, 0) + 1
            error_detail = "Iniciando servicio..."

        # 1. Guardar métrica en base de datos si hubo respuesta
        insert_health_metric(service_name, status_code, elapsed_ms, is_error)

        # 2. Calcular ventana móvil de métricas
        recent_metrics = get_recent_metrics(service_name, limit=ROLLING_WINDOW_SIZE)
        if recent_metrics:
            total_samples = len(recent_metrics)
            error_samples = sum(1 for m in recent_metrics if m["is_error"] == 1)
            error_rate = error_samples / total_samples
            avg_latency = sum(m["latency_ms"] for m in recent_metrics) / total_samples
        else:
            error_rate = 1.0 if is_error else 0.0
            avg_latency = elapsed_ms

        # 3. Evaluar estado de salud
        failures = self.consecutive_failures.get(service_name, 0)
        service_status = "HEALTHY"
        
        if failures >= 2 or (status_code in (0, 503, 504) and failures >= 1):
            service_status = "DOWN"
        elif avg_latency > latency_threshold or error_rate > error_threshold or is_error:
            service_status = "DEGRADED"

        # 4. Actualizar tabla de servicios
        upsert_service_status(
            name=service_name,
            status=service_status,
            last_latency=round(elapsed_ms, 2),
            avg_latency=round(avg_latency, 2),
            error_rate=round(error_rate, 4),
            uptime_seconds=uptime_seconds,
            active_faults=active_faults
        )

        # 5. Detección y Creación de Incidentes
        await self._evaluate_incident_triggers(
            service_name=service_name,
            service_status=service_status,
            status_code=status_code,
            last_latency=elapsed_ms,
            avg_latency=avg_latency,
            error_rate=error_rate,
            latency_threshold=latency_threshold,
            error_threshold=error_threshold,
            error_detail=error_detail
        )

    async def _evaluate_incident_triggers(
        self,
        service_name: str,
        service_status: str,
        status_code: int,
        last_latency: float,
        avg_latency: float,
        error_rate: float,
        latency_threshold: float,
        error_threshold: float,
        error_detail: str = None
    ):
        failures = self.consecutive_failures.get(service_name, 0)
        
        # Requiere al menos 2 fallos consecutivos para evitar falsas alarmas durante el arranque inicial
        if service_status == "DOWN" and failures >= 2:
            existing = get_open_incident_for_service(service_name, incident_type="OUTAGE")
            if not existing:
                logs_sample = get_container_logs(service_name, tail=20)
                inc_id = create_incident(
                    service_name=service_name,
                    title=f"Service Outage: {service_name.upper()} no responde (Caída)",
                    description=f"Health probe falló con código {status_code}. Detalle: {error_detail or 'Conexión rechazada'}.",
                    incident_type="OUTAGE",
                    severity="CRITICAL",
                    latency_ms=last_latency,
                    error_rate=error_rate,
                    logs_sample=logs_sample
                )
                logger.warning(f"[INCIDENT CREATED] Outage on {service_name} (ID #{inc_id})")
                asyncio.create_task(ai_agent.auto_diagnose_incident(inc_id))
            return

        if avg_latency > latency_threshold or last_latency > latency_threshold:
            existing = get_open_incident_for_service(service_name, incident_type="HIGH_LATENCY")
            if not existing:
                logs_sample = get_container_logs(service_name, tail=20)
                inc_id = create_incident(
                    service_name=service_name,
                    title=f"Latencia Elevada: {service_name.upper()} ({last_latency:.1f}ms > {latency_threshold:.0f}ms)",
                    description=f"El tiempo de respuesta superó el umbral configurado de {latency_threshold:.0f}ms. Promedio actual: {avg_latency:.1f}ms.",
                    incident_type="HIGH_LATENCY",
                    severity="WARNING",
                    latency_ms=last_latency,
                    error_rate=error_rate,
                    logs_sample=logs_sample
                )
                logger.warning(f"[INCIDENT CREATED] High latency on {service_name} (ID #{inc_id})")
                asyncio.create_task(ai_agent.auto_diagnose_incident(inc_id))
            return

        if error_rate > error_threshold and failures >= 1:
            existing = get_open_incident_for_service(service_name, incident_type="HIGH_ERROR_RATE")
            if not existing:
                logs_sample = get_container_logs(service_name, tail=20)
                inc_id = create_incident(
                    service_name=service_name,
                    title=f"Tasa de Errores Elevada: {service_name.upper()} ({(error_rate*100):.1f}% > {(error_threshold*100):.0f}%)",
                    description=f"La tasa de respuestas 500 superó el umbral de {(error_threshold*100):.0f}%.",
                    incident_type="HIGH_ERROR_RATE",
                    severity="CRITICAL",
                    latency_ms=last_latency,
                    error_rate=error_rate,
                    logs_sample=logs_sample
                )
                logger.warning(f"[INCIDENT CREATED] High error rate on {service_name} (ID #{inc_id})")
                asyncio.create_task(ai_agent.auto_diagnose_incident(inc_id))
            return

        if service_status == "HEALTHY" and avg_latency < latency_threshold and error_rate <= (error_threshold / 2.0):
            auto_resolve_open_incidents_for_service(
                service_name=service_name,
                note=f"Resolución automática: Latencia ({avg_latency:.1f}ms) y Tasa de Errores ({(error_rate*100):.1f}%) normalizadas."
            )

monitor = ServiceMonitor()
