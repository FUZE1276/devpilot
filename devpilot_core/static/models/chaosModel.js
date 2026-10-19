/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/chaosModel.js
 * Propósito: Entidad de inyección controlada de caos (latencia artificial, tasas de fallo 500, crash y reset).
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const ChaosModel = {
    async injectFault(payload) {
      return await window.DevPilot.Model.ApiClient.request('/api/fault/inject', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    }
  };

  window.DevPilot.Model.ChaosModel = ChaosModel;
})(window);
