/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/remediationModel.js
 * Propósito: Gestión de ciclo de vida de propuestas de auto-remediación asistida por IA,
 * aprobación con Step-Up TOTP, ejecución directa Docker SDK y bitácora forense de auditoría.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const RemediationModel = {
    async approveProposal(proposalId, notes, totpCode) {
      return await window.DevPilot.Model.ApiClient.request(`/api/remediation/proposals/${proposalId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes, totpCode })
      });
    },

    async rejectProposal(proposalId, notes) {
      return await window.DevPilot.Model.ApiClient.request(`/api/remediation/proposals/${proposalId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ notes })
      });
    },

    async executeDirect(service, action, incidentId, totpCode) {
      return await window.DevPilot.Model.ApiClient.request('/api/remediation/execute', {
        method: 'POST',
        body: JSON.stringify({ service, action, incidentId, totpCode })
      });
    },

    async getAuditHistory(limit = 50) {
      return await window.DevPilot.Model.ApiClient.request(`/api/audit/history?limit=${limit}`);
    }
  };

  window.DevPilot.Model.RemediationModel = RemediationModel;
})(window);
