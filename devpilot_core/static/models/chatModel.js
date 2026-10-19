/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/chatModel.js
 * Propósito: Comunicación bidireccional con el Copiloto SRE de IA (Claude / Heurístico Local)
 * e historial persistido de consultas causales.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const ChatModel = {
    async send(message) {
      return await window.DevPilot.Model.ApiClient.request('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ message })
      });
    },

    async getHistory() {
      return await window.DevPilot.Model.ApiClient.request('/api/ai/history');
    }
  };

  window.DevPilot.Model.ChatModel = ChatModel;
})(window);
