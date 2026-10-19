/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/model.js
 * Propósito: Punto de agregación y consolidación de la capa Modelo del patrón MVVM.
 * Expone window.DevPilot.Model y window.DevPilotModel para consumo desacoplado.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};

  const Model = {
    get ApiClient() { return window.DevPilot.Model.ApiClient; },
    get AuthModel() { return window.DevPilot.Model.AuthModel; },
    get TelemetryModel() { return window.DevPilot.Model.TelemetryModel; },
    get ChaosModel() { return window.DevPilot.Model.ChaosModel; },
    get RemediationModel() { return window.DevPilot.Model.RemediationModel; },
    get ServicesModel() { return window.DevPilot.Model.ServicesModel; },
    get LogsModel() { return window.DevPilot.Model.LogsModel; },
    get ChatModel() { return window.DevPilot.Model.ChatModel; }
  };

  // Asignar en namespace global
  Object.assign(window.DevPilot.Model, Model);
  window.DevPilotModel = window.DevPilot.Model;

  console.log('[DevPilot MVVM] Capa Modelo (Model) inicializada correctamente.');
})(window);
