/**
 * DevPilot SRE Platform - Capa Modelo (Model)
 * Archivo: models/authModel.js
 * Propósito: Entidad y cliente de red para autenticación (contraseña, MFA Email-OTP, SSO OIDC),
 * verificación TOTP RFC 6238 y gobernanza de roles/permisos RBAC.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};
  window.DevPilot.Model = window.DevPilot.Model || {};

  const AuthModel = {
    async loginWithPassword(username, password, emailOtpCode = null) {
      return await window.DevPilot.Model.ApiClient.request('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password, emailOtpCode })
      });
    },

    async requestEmailOtp(email) {
      return await window.DevPilot.Model.ApiClient.request('/api/auth/email-otp/request', {
        method: 'POST',
        body: JSON.stringify({ email })
      });
    },

    async loginSSO(email, role = null) {
      return await window.DevPilot.Model.ApiClient.request('/api/auth/sso/login', {
        method: 'POST',
        body: JSON.stringify({ email, role, provider: 'github_oidc' })
      });
    },

    async listUsers() {
      return await window.DevPilot.Model.ApiClient.request('/api/auth/users');
    },

    async updateUserPermissions(identifier, permissions) {
      return await window.DevPilot.Model.ApiClient.request(`/api/users/${encodeURIComponent(identifier)}/permissions`, {
        method: 'PUT',
        body: JSON.stringify({ permissions })
      });
    },

    async resetUserPermissions(identifier) {
      return await window.DevPilot.Model.ApiClient.request(`/api/users/${encodeURIComponent(identifier)}/permissions/reset`, {
        method: 'POST'
      });
    },

    async getMe() {
      return await window.DevPilot.Model.ApiClient.request('/api/auth/me');
    },

    async verifyTotp(code, secret = 'JBSWY3DPEHPK3PXP') {
      return await window.DevPilot.Model.ApiClient.request('/api/auth/verify-totp', {
        method: 'POST',
        body: JSON.stringify({ code, secret })
      });
    },

    async getDemoTotp(secret = 'JBSWY3DPEHPK3PXP') {
      return await window.DevPilot.Model.ApiClient.request(`/api/auth/demo-totp?secret=${encodeURIComponent(secret)}`);
    }
  };

  window.DevPilot.Model.AuthModel = AuthModel;
})(window);
