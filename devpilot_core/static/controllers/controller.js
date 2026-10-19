/**
 * DevPilot SRE Platform - Capa Controlador (Controller)
 * Archivo: controllers/controller.js
 * Propósito: Punto de entrada complementario y alias para la capa de controladores.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  if (window.DevPilotController) {
    window.DevPilot.Controller = window.DevPilotController;
    window.DevPilot.ViewModel = window.DevPilotController;
  }
})(window);
