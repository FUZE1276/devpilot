/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/telemetryModel.js
 * Propósito: Extracción de datos de telemetría en tiempo real, métricas agregadas por microservicio
 * y mutaciones de estado sobre incidentes del clúster.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const TelemetryModel = {
    async getSummary() {
      return await window.DevPilot.Model.ApiClient.request('/api/dashboard/summary');
    },

    async getMetrics(serviceName, limit = 30) {
      return await window.DevPilot.Model.ApiClient.request(`/api/metrics/${serviceName}?limit=${limit}`);
    },

    async resolveIncident(incidentId, note = "Resuelto manualmente") {
      return await window.DevPilot.Model.ApiClient.request(`/api/incidents/${incidentId}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ note })
      });
    }
  };

  window.DevPilot.Model.TelemetryModel = TelemetryModel;
})(window);
