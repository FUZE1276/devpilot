/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/logsModel.js
 * Propósito: Extracción de secuencias de registros (stdout/stderr) de contenedores Docker en vivo.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const LogsModel = {
    async getLogs(serviceName, tail = 120) {
      return await window.DevPilot.Model.ApiClient.request(`/api/logs/${serviceName}?tail=${tail}`);
    }
  };

  window.DevPilot.Model.LogsModel = LogsModel;
})(window);
