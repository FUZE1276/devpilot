/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/apiClient.js
 * Propósito: Cliente HTTP asíncrono con inyección automática de token JWT
 * e interceptores de respuesta para control de errores de red.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const ApiClient = {
    getToken() {
      return sessionStorage.getItem('devpilot_jwt_token') || '';
    },
    setToken(token) {
      if (token) {
        sessionStorage.setItem('devpilot_jwt_token', token);
      } else {
        sessionStorage.removeItem('devpilot_jwt_token');
      }
    },
    async request(url, options = {}) {
      const token = this.getToken();
      const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const res = await fetch(url, { ...options, headers });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detailMsg = data.detail || data.message || `Error HTTP ${res.status}`;
        const err = new Error(detailMsg);
        err.status = res.status;
        err.data = data;
        throw err;
      }
      return data;
    }
  };

  window.DevPilot.Model.ApiClient = ApiClient;
})(window);
