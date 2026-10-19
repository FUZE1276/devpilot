/**
 * DevPilot SRE Platform - Orquestador y Punto de Arranque SPA
 * Archivo: js/app.js
 * Propósito: Inicializar el framework MVVM unificado (Model, Controller/ViewModel, View)
 * al dispararse el evento DOMContentLoaded del navegador.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};

  // Consolidación de capas del patrón MVVM
  window.DevPilot.Model = window.DevPilot.Model || window.DevPilotModel;
  window.DevPilot.Controller = window.DevPilot.Controller || window.DevPilotController;
  window.DevPilot.ViewModel = window.DevPilot.Controller; // Alias MVVM
  window.DevPilot.View = window.DevPilot.View || window.DevPilotView;

  window.DevPilot.init = function() {
    console.log("🚀 [DevPilot MVVM Engine] Inicializando plataforma modular...");
    if (window.DevPilot.Controller && typeof window.DevPilot.Controller.initCommand === 'function') {
      window.DevPilot.Controller.initCommand();
    }
  };

  // Inicialización del framework al cargar la página
  window.addEventListener('DOMContentLoaded', () => {
    window.DevPilot.init();
  });
})(window);
