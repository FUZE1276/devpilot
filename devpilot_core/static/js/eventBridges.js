/**
 * DevPilot SRE Platform - Puentes Globales de Eventos y Manejadores DOM
 * Archivo: js/eventBridges.js
 * Propósito: Conectar los eventos declarativos del HTML (onclick, onsubmit, onchange)
 * con los comandos del Controlador/ViewModel y métodos de la Vista.
 */

// ==========================================
// PUENTES GLOBALES PARA MODALES Y GOBERNANZA
// ==========================================
function openNewServiceModal() { window.DevPilot.View.openNewServiceModal(); }
function closeNewServiceModal() { window.DevPilot.View.closeNewServiceModal(); }
function openAuditModal() { window.DevPilot.View.openAuditModal(); }
function closeAuditModal() { window.DevPilot.View.closeAuditModal(); }
function downloadAuditFile(f) { window.DevPilot.View.downloadAuditLog(f); }
function openUsersModal() { window.DevPilot.View.openUsersModal(); }
function closeUsersModal() { window.DevPilot.View.closeUsersModal(); }
function selectGovernanceUser(e) { window.DevPilot.View.selectGovernanceUser(e); }
function toggleGovPerm(p, c) { window.DevPilot.View.toggleGovPerm(p, c); }
function selectAllGovPerms(v) { window.DevPilot.View.selectAllGovPerms(v); }
function saveSelectedUserGovPerms() { window.DevPilot.View.saveGovernancePermissions(); }
function resetSelectedUserGovPerms() { window.DevPilot.View.resetGovernancePermissions(); }
function openLogsModal(s) { window.DevPilot.View.openLogsModal(s); }
function closeLogsModal() { window.DevPilot.View.closeLogsModal(); }
function openThresholdModal(s, l, e) { window.DevPilot.View.openThresholdModal(s, l, e); }
function closeThresholdModal() { window.DevPilot.View.closeThresholdModal(); }

// ==========================================
// AUTO-DESCUBRIMIENTO DE CONTENEDORES DOCKER
// ==========================================
let _discoveredCandidates = [];

function toggleTechnicalDetails() {
  const container = document.getElementById('technicalDetailsContainer');
  const toggleText = document.getElementById('toggleTechnicalText');
  if (!container) return;
  const isHidden = container.classList.contains('hidden');
  container.classList.toggle('hidden');
  if (toggleText) toggleText.innerText = isHidden ? 'Ocultar' : 'Ver / Editar';
}

async function scanDockerServices() {
  const loadingEl = document.getElementById('discoveredServicesLoading');
  const listEl = document.getElementById('discoveredServicesList');
  if (loadingEl) loadingEl.classList.remove('hidden');
  if (listEl) listEl.innerHTML = '';

  try {
    const res = await window.DevPilot.Model.ServicesModel.discover();
    if (loadingEl) loadingEl.classList.add('hidden');

    if (!res.success || !res.candidates || res.candidates.length === 0) {
      if (listEl) {
        listEl.innerHTML = `
          <div class="p-3.5 rounded-xl bg-dark-900 border border-slate-800 text-center text-slate-400 text-xs">
            <p class="font-medium text-slate-300">No se detectaron nuevos contenedores sin registrar.</p>
            <p class="text-[11px] text-slate-500 mt-0.5">Todos los servicios en ejecución ya están monitoreados o puedes ingresar los datos manualmente.</p>
          </div>
        `;
      }
      return;
    }

    _discoveredCandidates = res.candidates;
    let html = '';
    res.candidates.forEach((cand, idx) => {
      const healthBadge = cand.health_detected
        ? `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">✓ GET /health (200 OK • ${cand.latency_ms}ms)</span>`
        : `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px]">Puerto ${cand.port} activo</span>`;

      html += `
        <div onclick="selectDiscoveredService(${idx})" class="p-3 rounded-xl border border-slate-800 bg-dark-900 hover:border-indigo-500/60 hover:bg-indigo-950/20 transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 group">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-mono font-bold text-white text-xs">${cand.container_name}</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-indigo-500/20 text-indigo-300">:${cand.port}</span>
              ${healthBadge}
            </div>
            <p class="text-[11px] text-slate-400 font-mono">${cand.url} • <span class="text-cyan-400 font-semibold">${cand.suggested_type}</span></p>
          </div>
          <button type="button" class="px-3 py-1.5 rounded-lg bg-indigo-600 group-hover:bg-indigo-500 text-white font-semibold text-xs transition shadow flex items-center justify-center gap-1 shrink-0">
            <span>Auto-Rellenar</span>
            <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      `;
    });
    if (listEl) listEl.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();

    // Si hay un único candidato detectado, auto-seleccionarlo directamente
    if (res.candidates.length === 1) {
      selectDiscoveredService(0);
    }
  } catch (err) {
    if (loadingEl) loadingEl.classList.add('hidden');
    if (listEl) {
      listEl.innerHTML = `
        <div class="p-3 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 text-xs text-center">
          Error escaneando Docker: ${err.message || 'Verifica permisos o conexión con el socket'}.
        </div>
      `;
    }
  }
}

function selectDiscoveredService(idx) {
  const cand = _discoveredCandidates[idx];
  if (!cand) return;

  const slugInput = document.getElementById('newServiceSlug');
  const nameInput = document.getElementById('newServiceName');
  const typeInput = document.getElementById('newServiceType');
  const containerInput = document.getElementById('newServiceContainer');
  const urlInput = document.getElementById('newServiceUrl');

  if (slugInput) slugInput.value = cand.suggested_slug || '';
  if (nameInput) nameInput.value = cand.suggested_name || '';
  if (typeInput) typeInput.value = cand.suggested_type || 'Python';
  if (containerInput) containerInput.value = cand.container_name || '';
  if (urlInput) urlInput.value = cand.url || '';

  const banner = document.getElementById('selectedContainerBanner');
  const bannerText = document.getElementById('selectedContainerBannerText');
  if (banner && bannerText) {
    bannerText.innerHTML = `Contenedor <strong class="text-white">${cand.container_name}</strong> vinculado con URL <span class="font-mono text-cyan-300">${cand.url}</span>. Solo revisa el nombre y los SLAs.`;
    banner.classList.remove('hidden');
  }

  if (nameInput) {
    nameInput.focus();
    nameInput.select();
  }
  showToast(`Datos técnicos auto-completados para ${cand.container_name}`, 'success');
}

async function handleNewServiceSubmit(e) {
  if (e) e.preventDefault();
  const slug = document.getElementById('newServiceSlug')?.value.trim();
  const name = document.getElementById('newServiceName')?.value.trim();
  const type = document.getElementById('newServiceType')?.value.trim();
  const container = document.getElementById('newServiceContainer')?.value.trim();
  const url = document.getElementById('newServiceUrl')?.value.trim();
  const latVal = parseFloat(document.getElementById('newServiceLatencyRange')?.value || '2000');
  const errVal = parseFloat(document.getElementById('newServiceErrorRange')?.value || '20') / 100.0;

  if (!slug || !name || !url || !container) {
    showToast("Por favor completa los campos requeridos.", "warning");
    return;
  }

  try {
    const res = await window.DevPilot.Model.ServicesModel.register({
      name: slug,
      displayName: name,
      serviceType: type || 'Custom',
      containerName: container,
      url: url,
      latencyThresholdMs: latVal,
      errorThresholdPct: errVal
    });
    if (res.success) {
      showToast(res.message || `Servicio '${name}' registrado y monitoreado exitosamente`, "success");
      closeNewServiceModal();
      document.getElementById('newServiceSlug').value = '';
      document.getElementById('newServiceName').value = '';
      document.getElementById('newServiceType').value = '';
      document.getElementById('newServiceContainer').value = '';
      document.getElementById('newServiceUrl').value = '';
      document.getElementById('selectedContainerBanner')?.classList.add('hidden');
      setTimeout(() => window.DevPilot.Controller.pollTelemetryCommand(), 500);
    } else {
      showToast(res.detail || "Error registrando servicio", "error");
    }
  } catch (err) {
    showToast(err.message || "Error al conectar con la API", "error");
  }
}

async function saveServiceThresholds(e) {
  if (e) e.preventDefault();
  const targetService = document.getElementById('thresholdTargetService')?.value;
  const latVal = parseFloat(document.getElementById('modalLatencyRange')?.value || '2000');
  const errVal = parseFloat(document.getElementById('modalErrorRange')?.value || '20') / 100.0;

  if (!targetService) return;

  try {
    const res = await window.DevPilot.Model.ServicesModel.updateThresholds(targetService, latVal, errVal);
    if (res.success) {
      showToast(res.message || "Umbrales actualizados exitosamente", "success");
      closeThresholdModal();
      setTimeout(() => window.DevPilot.Controller.pollTelemetryCommand(), 500);
    } else {
      showToast(res.detail || "Error actualizando umbrales", "error");
    }
  } catch (err) {
    showToast(err.message || "Error al conectar con la API", "error");
  }
}

// ==========================================
// PUENTES DE COMANDOS DEL CONTROLADOR
// ==========================================
function manualRefresh() { window.DevPilot.Controller.pollTelemetryCommand(); }
function injectPresetFault(type) { window.DevPilot.Controller.injectChaosCommand(type); }
function applyCustomFault() { window.DevPilot.Controller.applyCustomChaosCommand(); }
function resetAllServicesChaos() { window.DevPilot.Controller.resetAllChaosCommand(); }
function approveProposal(id) { window.DevPilot.Controller.requestProposalApprovalCommand(id); }
function rejectProposal(id) { window.DevPilot.Controller.rejectProposalCommand(id); }
function remediateWithDockerSDK(s, a, id) { window.DevPilot.Controller.requestDirectRemediationCommand(s, a, id); }
function closeRemediationModal() { window.DevPilot.View.closeRemediationModal(); }

function filterIncidents(filter) {
  window.DevPilot.Controller.state.incidentFilter = filter;
  ['filterAllBtn', 'filterOpenBtn', 'filterResolvedBtn'].forEach(b => {
    const el = document.getElementById(b);
    if (el) el.className = 'px-2 py-0.5 rounded text-slate-400 hover:text-white';
  });
  const activeBtn = filter === 'ALL' ? 'filterAllBtn' : (filter === 'OPEN' ? 'filterOpenBtn' : 'filterResolvedBtn');
  const activeEl = document.getElementById(activeBtn);
  if (activeEl) activeEl.className = 'px-2 py-0.5 rounded bg-indigo-600 text-white font-medium';
  window.DevPilot.View.renderIncidents(window.DevPilot.Controller.state.incidents, filter);
}

function sendQuickPrompt(t) { window.DevPilot.View.sendQuickPrompt(t); }

function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  window.DevPilot.Controller.sendChatCommand(input.value);
  input.value = '';
}

function clearChatUI() {
  document.getElementById('chatMessages').innerHTML = '<div class="text-center py-4 text-slate-500 text-xs">Historial de chat limpiado.</div>';
}

// ==========================================
// FUNCIONES DEL FORMULARIO DE ACCESO Y DOBLE FACTOR
// ==========================================
function fillLoginCredentials(user, pass) {
  const uInput = document.getElementById('loginUsername');
  const pInput = document.getElementById('loginPassword');
  if (uInput) uInput.value = user;
  if (pInput) pInput.value = pass;
  window.DevPilot.View.clearLoginError();
  if (pInput) pInput.focus();
}

function togglePasswordVisibility() {
  const pInput = document.getElementById('loginPassword');
  const icon = document.getElementById('eyeIcon');
  if (!pInput) return;
  if (pInput.type === 'password') {
    pInput.type = 'text';
    if (icon) icon.setAttribute('data-lucide', 'eye-off');
  } else {
    pInput.type = 'password';
    if (icon) icon.setAttribute('data-lucide', 'eye');
  }
  lucide.createIcons();
}

function handleCredentialsLogin(e) {
  if (e) e.preventDefault();
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!username || !password) {
    window.DevPilot.View.showLoginError("Por favor ingrese el usuario y la contraseña.");
    return;
  }
  window.DevPilot.Controller.loginWithCredentialsCommand(username, password);
}

function handleEmailOtpSubmit(e) {
  if (e) e.preventDefault();
  const code = document.getElementById('emailOtpInput').value.trim();
  if (!code || code.length !== 6) {
    window.DevPilot.View.showEmailOtpError("Por favor ingresa el código numérico de 6 dígitos.");
    return;
  }
  window.DevPilot.Controller.submitEmailOtpCommand(code);
}

function handleResendEmailOtp() {
  window.DevPilot.Controller.resendEmailOtpCommand();
}

function cancelEmailOtpStep() {
  window.DevPilot.Controller.cancelEmailOtpCommand();
}

function pasteDevEmailOtp() {
  const devText = document.getElementById('emailOtpDevText');
  const code = devText?.getAttribute('data-code') || devText?.innerText?.match(/\d{6}/)?.[0];
  const input = document.getElementById('emailOtpInput');
  if (code && input) {
    input.value = code;
    window.DevPilot.View.clearEmailOtpError();
    input.focus();
  }
}

// ==========================================
// TOAST GLOBAL DE NOTIFICACIÓN
// ==========================================
let _toastTimer = null;
function showToast(msg, type = 'success') {
  const toast = document.getElementById('devpilot-toast');
  const toastMsg = document.getElementById('devpilot-toast-msg');
  const toastIcon = document.getElementById('devpilot-toast-icon');
  if (!toast || !toastMsg) return;
  toastMsg.innerText = msg;
  toast.className = `show ${type}`;
  const iconMap = { success: 'check-circle', error: 'alert-circle', warning: 'alert-triangle' };
  if (toastIcon) toastIcon.setAttribute('data-lucide', iconMap[type] || 'info');
  if (window.lucide) window.lucide.createIcons();
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { toast.className = ''; }, 4000);
}

// Funciones no-op para retrocompatibilidad con scripts residuales
function switchBizTab() {}
function runSmokeTest() {}
function loadBizData() {}
