/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/servicesModel.js
 * Propósito: Catálogo de microservicios monitoreados, descubrimiento automático de contenedores Docker
 * en devpilot_net, registro dinámico y calibración de umbrales SLA.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const ServicesModel = {
    async list() {
      return await window.DevPilot.Model.ApiClient.request('/api/services');
    },

    async discover() {
      return await window.DevPilot.Model.ApiClient.request('/api/services/discover');
    },

    async register(payload) {
      return await window.DevPilot.Model.ApiClient.request('/api/services', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    },

    async updateThresholds(name, latencyMs, errorPct) {
      return await window.DevPilot.Model.ApiClient.request(`/api/services/${name}/thresholds`, {
        method: 'PUT',
        body: JSON.stringify({ latencyThresholdMs: latencyMs, errorThresholdPct: errorPct })
      });
    }
  };

  window.DevPilot.Model.ServicesModel = ServicesModel;
})(window);
