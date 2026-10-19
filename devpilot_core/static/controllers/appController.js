/**
 * DevPilot SRE Platform - Capa Controlador / Vista-Modelo (Controller / ViewModel)
 * Archivo: controllers/appController.js
 * Propósito: Gestiona el estado observable de la aplicación, propiedades computadas,
 * comandos ejecutables (Command Pattern) y el bus de eventos observadores (Observer Pattern).
 * Se expone como window.DevPilot.Controller y window.DevPilot.ViewModel.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};

  const POLLING_INTERVAL = 3000;

  const Controller = {
    // ==========================================
    // 1. ESTADO REACTIVO OBSERVABLE (STATE STORE)
    // ==========================================
    state: {
      currentUser: null,
      services: [],
      incidents: [],
      proposals: [],
      system: { ai: {}, docker_connected: true },
      metrics: {},
      incidentFilter: 'ALL',
      pendingTotpAction: null,
      currentLogsService: null,
      isPolling: true
    },

    // ==========================================
    // 2. PROPIEDADES COMPUTADAS
    // ==========================================
    computed: {
      isChaosAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('chaos:inject');
      },
      isRemediationAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('remediation:execute');
      },
      isThresholdsAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('thresholds:write');
      },
      isAuditAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('audit:read');
      },
      isLogsAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('logs:read');
      },
      isIncidentsManageAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('incidents:manage') || perms.includes('remediation:execute');
      },
      isUsersManageAllowed() {
        const perms = Controller.state.currentUser?.permissions || [];
        return perms.includes('users:manage');
      },
      clusterStatus() {
        const s = Controller.state.services;
        if (!s || s.length === 0) return 'UNKNOWN';
        if (s.some(x => x.status === 'DOWN')) return 'CRITICAL';
        if (s.some(x => x.status === 'DEGRADED')) return 'DEGRADED';
        return 'HEALTHY';
      },
      avgLatency() {
        const s = Controller.state.services;
        if (!s || s.length === 0) return 0;
        const sum = s.reduce((acc, x) => acc + Number(x.last_latency || 0), 0);
        return Math.round(sum / s.length);
      }
    },

    // ==========================================
    // 3. BUS DE EVENTOS OBSERVADOR (OBSERVER PATTERN)
    // ==========================================
    listeners: {},
    subscribe(event, callback) {
      if (!this.listeners[event]) this.listeners[event] = [];
      this.listeners[event].push(callback);
    },
    notify(event, data) {
      if (this.listeners[event]) {
        this.listeners[event].forEach(cb => {
          try {
            cb(data);
          } catch(e) {
            console.error(`[DevPilot Controller] Error en listener del evento '${event}':`, e);
          }
        });
      }
    },

    // ==========================================
    // 4. COMANDOS EJECUTABLES (COMMAND PATTERN)
    // ==========================================
    pollingTimer: null,

    startPollingLoop() {
      if (this.pollingTimer) clearInterval(this.pollingTimer);
      this.pollingTimer = setInterval(() => {
        if (Controller.state.isPolling && window.DevPilot.Model.ApiClient.getToken()) {
          Controller.pollTelemetryCommand();
        }
      }, POLLING_INTERVAL);
    },

    async initCommand() {
      // Exigir siempre inicio de sesión con credenciales al entrar a la plataforma
      window.DevPilot.Model.ApiClient.setToken('');
      sessionStorage.removeItem('devpilot_jwt_token');
      sessionStorage.removeItem('devpilot_sso_email');
      this.state.currentUser = null;
      if (window.DevPilot.View) {
        window.DevPilot.View.showLoginPortal();
      }
    },

    async loginWithCredentialsCommand(username, password) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      try {
        if (View) View.clearLoginError();
        const res = await Model.AuthModel.loginWithPassword(username, password);
        if (res.requires_email_otp) {
          // Guardar credenciales temporalmente para el paso de doble factor (MFA)
          this.state.pendingLogin = { username, password, email: res.email, dev_code: res.dev_code };
          if (View) View.showEmailOtpStep(res.email, res.dev_code, res.message, res.destination_email);
          return;
        }
        if (res.success && res.access_token) {
          Model.ApiClient.setToken(res.access_token);
          sessionStorage.setItem('devpilot_sso_email', res.user.email);
          this.state.currentUser = res.user;

          if (View) {
            View.hideLoginPortal();
            View.initChart();
          }
          this.notify('auth:changed', this.state.currentUser);
          await this.pollTelemetryCommand();
          this.startPollingLoop();
          if (View) View.showNotification(`¡Sesión iniciada! Bienvenido, ${res.user.name} (Rol: ${res.user.role})`, true);
        } else {
          if (View) View.showLoginError(res.detail || "Usuario o contraseña incorrectos.");
        }
      } catch (err) {
        if (View) View.showLoginError(err.message || "Usuario o contraseña incorrectos.");
      }
    },

    async submitEmailOtpCommand(code) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      if (!this.state.pendingLogin) {
        if (View) View.showEmailOtpError("Sesión de login no encontrada. Vuelve a ingresar credenciales.");
        return;
      }
      const { username, password } = this.state.pendingLogin;
      try {
        if (View) View.clearEmailOtpError();
        const res = await Model.AuthModel.loginWithPassword(username, password, code);
        if (res.success && res.access_token) {
          Model.ApiClient.setToken(res.access_token);
          sessionStorage.setItem('devpilot_sso_email', res.user.email);
          this.state.currentUser = res.user;
          this.state.pendingLogin = null;

          if (View) {
            View.hideEmailOtpStep();
            View.hideLoginPortal();
            View.initChart();
          }
          this.notify('auth:changed', this.state.currentUser);
          await this.pollTelemetryCommand();
          this.startPollingLoop();
          if (View) View.showNotification(`¡Segundo factor verificado! Bienvenido, ${res.user.name} (Rol: ${res.user.role})`, true);
        } else {
          if (View) View.showEmailOtpError(res.detail || "Código de verificación inválido.");
        }
      } catch (err) {
        if (View) View.showEmailOtpError(err.message || "Código incorrecto o expirado.");
      }
    },

    async resendEmailOtpCommand() {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      if (!this.state.pendingLogin) return;
      try {
        const res = await Model.AuthModel.requestEmailOtp(this.state.pendingLogin.email);
        if (res.success) {
          this.state.pendingLogin.dev_code = res.dev_code;
          if (View) {
            View.updateEmailOtpDevCode(res.dev_code);
            View.restartEmailOtpTimer();
            View.showNotification("Nuevo código de verificación generado.", true);
          }
        }
      } catch (err) {
        if (View) View.showEmailOtpError(err.message || "Error al reenviar código.");
      }
    },

    cancelEmailOtpCommand() {
      this.state.pendingLogin = null;
      if (window.DevPilot.View) window.DevPilot.View.hideEmailOtpStep();
    },

    async performLoginCommand(email, totpCode = null) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      try {
        if (View) View.clearLoginError();
        const res = await Model.AuthModel.loginSSO(email);
        if (res.success && res.access_token) {
          Model.ApiClient.setToken(res.access_token);
          sessionStorage.setItem('devpilot_sso_email', email);
          this.state.currentUser = res.user;

          if (totpCode && totpCode.trim().length === 6) {
            try {
              await Model.AuthModel.verifyTotp(totpCode.trim(), res.user.totp_secret || 'JBSWY3DPEHPK3PXP');
            } catch(te) {
              console.warn("Verificación TOTP inicial:", te);
            }
          }

          if (View) {
            View.hideLoginPortal();
            View.initChart();
          }
          this.notify('auth:changed', this.state.currentUser);
          await this.pollTelemetryCommand();
          this.startPollingLoop();
          if (View) View.showNotification(`¡Sesión iniciada! Bienvenido, ${res.user.name} (Rol: ${res.user.role})`, true);
        } else {
          if (View) View.showLoginError(res.detail || "Error en credenciales SSO");
        }
      } catch (err) {
        if (View) View.showLoginError(err.message || "Fallo de conexión en portal SSO");
      }
    },

    logoutCommand() {
      window.DevPilot.Model.ApiClient.setToken('');
      sessionStorage.removeItem('devpilot_sso_email');
      sessionStorage.removeItem('devpilot_jwt_token');
      this.state.currentUser = null;
      if (this.pollingTimer) clearInterval(this.pollingTimer);
      if (window.DevPilot.View) window.DevPilot.View.showLoginPortal();
    },

    switchUserCommand() {
      // Seguridad estricta: cambiar de rol exige nueva autenticación
      this.logoutCommand();
    },

    async pollTelemetryCommand() {
      const Model = window.DevPilot.Model;
      try {
        const res = await Model.TelemetryModel.getSummary();
        if (!res.success) return;

        if (res.services) this.state.services = res.services;
        if (res.incidents) this.state.incidents = res.incidents;
        if (res.proposals) this.state.proposals = res.proposals;
        if (res.system) this.state.system = res.system;
        if (res.metrics) this.state.metrics = res.metrics;

        this.notify('telemetry:updated', this.state);
      } catch (err) {
        console.error("[DevPilot Controller] Error en sondeo de telemetría:", err);
      }
    },

    async injectChaosCommand(type) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      if (!this.computed.isChaosAllowed()) {
        if (View) View.showNotification(`Acceso denegado (RBAC): El rol '${this.state.currentUser.role}' no posee el permiso 'chaos:inject'.`, false);
        return;
      }
      const service = document.getElementById('targetServiceSelect').value;
      let payload = { service, type };
      if (type === 'delay') payload.delayMs = 2500;
      if (type === 'error') payload.errorRate = 0.50;
      if (type === 'crash') payload.reason = "Simulated crash via DevPilot Chaos Studio";

      try {
        const res = await Model.ChaosModel.injectFault(payload);
        if (res.success) {
          if (View) View.showNotification(`Inyección '${type}' aplicada a ${service.toUpperCase()}`, true);
          setTimeout(() => this.pollTelemetryCommand(), 800);
        } else {
          if (View) View.showNotification(`Error inyectando fallo: ${res.error || res.detail}`, false);
        }
      } catch (err) {
        if (View) View.showNotification(`Error de red o RBAC: ${err.message}`, false);
      }
    },

    async applyCustomChaosCommand() {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      if (!this.computed.isChaosAllowed()) {
        if (View) View.showNotification(`Acceso denegado (RBAC): Rol actual '${this.state.currentUser.role}' no puede inyectar fallos.`, false);
        return;
      }
      const service = document.getElementById('targetServiceSelect').value;
      const delayMs = parseInt(document.getElementById('customDelayRange').value, 10);
      const errorPct = parseInt(document.getElementById('customErrorRange').value, 10);

      try {
        if (delayMs === 0 && errorPct === 0) {
          await Model.ChaosModel.injectFault({ service, type: 'reset' });
        } else {
          if (delayMs > 0) await Model.ChaosModel.injectFault({ service, type: 'delay', delayMs });
          if (errorPct > 0) await Model.ChaosModel.injectFault({ service, type: 'error', errorRate: errorPct / 100.0 });
        }
        if (View) View.showNotification(`Parámetros de caos aplicados a ${service.toUpperCase()}`, true);
        setTimeout(() => this.pollTelemetryCommand(), 800);
      } catch (err) {
        if (View) View.showNotification(`Error: ${err.message}`, false);
      }
    },

    async resetAllChaosCommand() {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      if (!this.computed.isChaosAllowed()) {
        if (View) View.showNotification(`Acceso denegado (RBAC): Rol '${this.state.currentUser.role}' sin permiso de caos.`, false);
        return;
      }
      try {
        for (const s of this.state.services) {
          await Model.ChaosModel.injectFault({ service: s.name, type: 'reset' });
        }
        if (View) View.showNotification("Reset de caos global completado.", true);
        setTimeout(() => this.pollTelemetryCommand(), 800);
      } catch (err) {
        if (View) View.showNotification(`Error: ${err.message}`, false);
      }
    },

    requestProposalApprovalCommand(proposalId) {
      const View = window.DevPilot.View;
      if (!this.computed.isRemediationAllowed()) {
        if (View) View.showNotification(`Acceso denegado (RBAC): Rol '${this.state.currentUser.role}' no posee permiso 'remediation:execute'.`, false);
        return;
      }
      const proposal = this.state.proposals.find(p => p.id === proposalId);
      this.state.pendingTotpAction = {
        type: 'proposal',
        id: proposalId,
        serviceName: proposal ? proposal.service_name : 'users',
        actionType: proposal ? proposal.action_type : 'RESTART_CONTAINER',
        description: `Aprobar Propuesta #${proposalId}: ${proposal ? proposal.action_type : 'RESTART'} en ${proposal ? proposal.service_name : 'servicio'}`
      };
      if (View) View.openTotpModal(this.state.pendingTotpAction);
    },

    requestDirectRemediationCommand(service, action = "RESTART_CONTAINER", incidentId = null) {
      const View = window.DevPilot.View;
      if (!this.computed.isRemediationAllowed()) {
        if (View) View.showNotification(`Acceso denegado (RBAC): Rol '${this.state.currentUser.role}' no posee permiso 'remediation:execute'.`, false);
        return;
      }
      this.state.pendingTotpAction = {
        type: 'direct',
        serviceName: service,
        actionType: action,
        incidentId: incidentId,
        description: `Auto-Remediación Directa: ${action} en contenedor '${service}'`
      };
      if (View) View.openTotpModal(this.state.pendingTotpAction);
    },

    async confirmRemediationWithTotpCommand() {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      const codeInput = document.getElementById('totpInputCode');
      const code = (codeInput?.value || '').trim();

      if (!code || code.length !== 6 || !/^\d+$/.test(code)) {
        if (View) View.showTotpError("Por favor ingrese un código TOTP numérico de 6 dígitos.");
        return;
      }

      const action = this.state.pendingTotpAction;
      if (!action) return;

      try {
        if (action.type === 'proposal') {
          await Model.RemediationModel.approveProposal(action.id, "Aprobado por operador SRE con TOTP", code);
        } else {
          await Model.RemediationModel.executeDirect(action.serviceName, action.actionType, action.incidentId, code);
        }

        if (View) {
          View.closeTotpModal();
          View.showNotification(`Remediación autorizada exitosamente mediante TOTP (${action.serviceName.toUpperCase()})`, true);
          View.runRemediationVisualPipeline(action.serviceName, action.actionType);
        }
      } catch (err) {
        if (View) View.showTotpError(err.message || "Código TOTP inválido o expirado.");
      }
    },

    async rejectProposalCommand(proposalId) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      if (!this.computed.isRemediationAllowed()) {
        if (View) View.showNotification(`Acceso denegado (RBAC): Rol '${this.state.currentUser.role}' no puede rechazar propuestas.`, false);
        return;
      }
      try {
        await Model.RemediationModel.rejectProposal(proposalId, "Rechazado por el operador técnico");
        if (View) View.showNotification(`Propuesta #${proposalId} rechazada.`, true);
        this.pollTelemetryCommand();
      } catch (err) {
        if (View) View.showNotification(`Error: ${err.message}`, false);
      }
    },

    async resolveIncidentCommand(incidentId) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      try {
        await Model.TelemetryModel.resolveIncident(incidentId, "Resuelto manualmente desde dashboard");
        if (View) View.showNotification(`Incidente #${incidentId} marcado como resuelto.`, true);
        this.pollTelemetryCommand();
      } catch (err) {
        if (View) View.showNotification(`Error: ${err.message}`, false);
      }
    },

    async sendChatCommand(message) {
      const View = window.DevPilot.View;
      const Model = window.DevPilot.Model;
      const msg = (message || '').trim();
      if (!msg) return;

      if (View) View.appendChatMessage('user', msg);
      try {
        const res = await Model.ChatModel.send(msg);
        if (res.success && res.data) {
          if (View) View.appendChatMessage('assistant', res.data.reply);
          this.pollTelemetryCommand();
        }
      } catch (err) {
        if (View) View.appendChatMessage('assistant', `Error de conexión con el agente: ${err.message}`);
      }
    }
  };

  // Exponer dualmente como Controller y ViewModel para máxima interoperabilidad
  window.DevPilot.Controller = Controller;
  window.DevPilot.ViewModel = Controller;
  window.DevPilotController = Controller;
  window.DevPilotViewModel = Controller;

  console.log('[DevPilot MVVM] Capa Controlador / ViewModel inicializada correctamente.');
})(window);
