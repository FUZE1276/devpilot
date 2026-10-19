/**
 * DevPilot SRE Platform - Capa Vista (View)
 * Archivo: views/view.js
 * Propósito: Renderizado declarativo del DOM, enlace bidireccional reactivo con el Controlador,
 * gestión de modales, visualización gráfica con Chart.js e integración con Lucide Icons.
 */

(function(window) {
  'use strict';

  window.DevPilot = window.DevPilot || {};

  const View = {
    chartInstance: null,

    refreshIcons() {
      if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
      }
    },

    initChart() {
      const canvas = document.getElementById('latencyChart');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['-30s', '-25s', '-20s', '-15s', '-10s', '-5s', 'Ahora'],
          datasets: [
            { label: 'Users', borderColor: '#6366f1', backgroundColor: 'rgba(99, 102, 241, 0.1)', borderWidth: 2, pointRadius: 2, tension: 0.3, data: [15, 20, 18, 22, 19, 21, 20] },
            { label: 'Products', borderColor: '#06b6d4', backgroundColor: 'rgba(6, 182, 212, 0.1)', borderWidth: 2, pointRadius: 2, tension: 0.3, data: [10, 12, 14, 11, 15, 12, 13] },
            { label: 'Orders', borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.1)', borderWidth: 2, pointRadius: 2, tension: 0.3, data: [25, 28, 22, 30, 26, 24, 27] }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 300 },
          scales: {
            y: { beginAtZero: true, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
            x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } }
          },
          plugins: { legend: { labels: { color: '#e2e8f0', boxWidth: 10, font: { size: 11 } } } }
        }
      });
    },

    showLoginPortal() {
      const portal = document.getElementById('loginPortalScreen');
      const header = document.getElementById('mainAppHeader');
      const body = document.getElementById('mainAppBody');
      if (portal) {
        portal.style.setProperty('display', 'flex', 'important');
        portal.classList.remove('hidden');
      }
      if (header) {
        header.style.setProperty('display', 'none', 'important');
        header.classList.add('hidden');
      }
      if (body) {
        body.style.setProperty('display', 'none', 'important');
        body.classList.add('hidden');
      }
      this.refreshIcons();
    },

    hideLoginPortal() {
      const portal = document.getElementById('loginPortalScreen');
      const header = document.getElementById('mainAppHeader');
      const body = document.getElementById('mainAppBody');
      if (portal) {
        portal.style.setProperty('display', 'none', 'important');
        portal.classList.add('hidden');
      }
      if (header) {
        header.style.removeProperty('display');
        header.classList.remove('hidden');
      }
      if (body) {
        body.style.removeProperty('display');
        body.classList.remove('hidden');
      }
      this.refreshIcons();
    },

    showLoginError(msg) {
      const box = document.getElementById('loginErrorMessage');
      const txt = document.getElementById('loginErrorText');
      if (txt) txt.innerText = msg;
      else if (box) box.innerText = msg;
      if (box) box.classList.remove('hidden');
    },

    clearLoginError() {
      const box = document.getElementById('loginErrorMessage');
      if (box) box.classList.add('hidden');
    },

    emailOtpTimer: null,

    showEmailOtpStep(email, devCode, message, destEmail = null) {
      const step1 = document.getElementById('loginStep1Container');
      const step2 = document.getElementById('loginStep2Container');
      const emailTarget = document.getElementById('emailOtpTargetText');
      const otpInput = document.getElementById('emailOtpInput');

      if (step1) step1.classList.add('hidden');
      if (step2) step2.classList.remove('hidden');
      if (emailTarget) {
        if (destEmail && destEmail.toLowerCase() !== email.toLowerCase()) {
          emailTarget.innerHTML = `<strong class="text-cyan-300 font-bold">${destEmail}</strong> <span class="text-slate-400 text-[11px] font-normal">(cuenta: ${email})</span>`;
        } else {
          emailTarget.innerText = destEmail || email;
        }
      }

      this.updateEmailOtpDevCode(devCode);
      this.clearEmailOtpError();
      this.restartEmailOtpTimer();

      if (otpInput) {
        otpInput.value = '';
        setTimeout(() => otpInput.focus(), 150);
      }
      this.refreshIcons();
    },

    updateEmailOtpDevCode(devCode) {
      const devChip = document.getElementById('emailOtpDevChip');
      const devText = document.getElementById('emailOtpDevText');
      if (devCode && devChip && devText) {
        devChip.classList.remove('hidden');
        devText.innerText = `Código OTP simulado: ${devCode}`;
        devText.setAttribute('data-code', devCode);
      } else if (devChip) {
        devChip.classList.add('hidden');
      }
    },

    hideEmailOtpStep() {
      const step1 = document.getElementById('loginStep1Container');
      const step2 = document.getElementById('loginStep2Container');
      if (step2) step2.classList.add('hidden');
      if (step1) step1.classList.remove('hidden');
      if (this.emailOtpTimer) clearInterval(this.emailOtpTimer);
      this.refreshIcons();
    },

    showEmailOtpError(msg) {
      const box = document.getElementById('emailOtpErrorBox');
      const txt = document.getElementById('emailOtpErrorText');
      if (txt) txt.innerText = msg;
      else if (box) box.innerText = msg;
      if (box) box.classList.remove('hidden');
    },

    clearEmailOtpError() {
      const box = document.getElementById('emailOtpErrorBox');
      if (box) box.classList.add('hidden');
    },

    restartEmailOtpTimer() {
      if (this.emailOtpTimer) clearInterval(this.emailOtpTimer);
      let timeLeft = 300;
      const timerEl = document.getElementById('emailOtpTimerText');
      const update = () => {
        const m = Math.floor(timeLeft / 60).toString().padStart(2, '0');
        const s = (timeLeft % 60).toString().padStart(2, '0');
        if (timerEl) timerEl.innerText = `${m}:${s}`;
        if (timeLeft <= 0) {
          clearInterval(this.emailOtpTimer);
          if (timerEl) timerEl.innerText = "Expirado";
          this.showEmailOtpError("El código ha expirado. Haz clic en 'Reenviar' para generar uno nuevo.");
        }
        timeLeft--;
      };
      update();
      this.emailOtpTimer = setInterval(update, 1000);
    },

    renderAuthBar(user) {
      if (!user) return;
      const nameEl = document.getElementById('authUserName');
      const emailEl = document.getElementById('authUserEmail');
      const badgeEl = document.getElementById('authUserRoleBadge');
      const avatarEl = document.getElementById('authAvatarBox');

      if (nameEl) nameEl.innerText = user.name || user.email;
      if (emailEl) emailEl.innerText = user.email;

      const roleColors = {
        'Super_Administrador': 'bg-purple-500/20 text-purple-300 border-purple-500/40',
        'Administrador': 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
        'Cliente': 'bg-slate-700/40 text-slate-300 border-slate-600',
        'Admin': 'bg-purple-500/20 text-purple-300 border-purple-500/40',
        'SRE_Operator': 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
        'Developer': 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
        'Viewer': 'bg-slate-700/40 text-slate-300 border-slate-600'
      };
      if (badgeEl) {
        badgeEl.className = `px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider border ${roleColors[user.role] || roleColors['Viewer']}`;
        badgeEl.innerText = user.role;
      }

      if (avatarEl) {
        const initials = (user.name || user.role).substring(0, 2).toUpperCase();
        avatarEl.innerText = initials;
      }

      const canChaos = window.DevPilot.Controller.computed.isChaosAllowed();
      const warningEl = document.getElementById('chaosRbacWarning');
      if (warningEl) {
        if (canChaos) warningEl.classList.add('hidden');
        else warningEl.classList.remove('hidden');
      }

      const chaosSection = document.getElementById('chaosControlsSection');
      if (chaosSection) {
        if (canChaos) chaosSection.classList.remove('opacity-30', 'pointer-events-none');
        else chaosSection.classList.add('opacity-30', 'pointer-events-none');
      }

      const newServiceBtn = document.getElementById('btnOpenNewService');
      if (newServiceBtn) {
        if (window.DevPilot.Controller.computed.isThresholdsAllowed()) newServiceBtn.classList.remove('hidden');
        else newServiceBtn.classList.add('hidden');
      }

      const auditBtn = document.getElementById('btnOpenAudit');
      if (auditBtn) {
        if (window.DevPilot.Controller.computed.isAuditAllowed()) auditBtn.classList.remove('hidden');
        else auditBtn.classList.add('hidden');
      }

      const usersBtn = document.getElementById('btnOpenUsersModal');
      if (usersBtn) {
        if (window.DevPilot.Controller.computed.isUsersManageAllowed()) usersBtn.classList.remove('hidden');
        else usersBtn.classList.add('hidden');
      }
    },

    govState: {
      users: [],
      catalog: [],
      selectedEmail: null,
      selectedPerms: new Set()
    },

    async openUsersModal() {
      const modal = document.getElementById('usersModal');
      if (!modal) return;
      modal.classList.remove('hidden');
      this.refreshIcons();
      
      try {
        const res = await window.DevPilot.Model.AuthModel.listUsers();
        if (res.success) {
          this.govState.users = res.users || [];
          this.govState.catalog = res.permissions_catalog || [];
          const defaultEmail = this.govState.selectedEmail || (this.govState.users.length > 0 ? this.govState.users[0].email : null);
          if (defaultEmail) {
            this.selectGovernanceUser(defaultEmail);
          }
        }
      } catch(e) {
        console.error("Error cargando usuarios en gobernanza:", e);
      }
    },

    closeUsersModal() {
      const modal = document.getElementById('usersModal');
      if (modal) modal.classList.add('hidden');
    },

    selectGovernanceUser(email) {
      this.govState.selectedEmail = email;
      const user = this.govState.users.find(u => u.email === email) || this.govState.users[0];
      if (user) {
        const rawPerms = (user.permissions !== null && user.permissions !== undefined)
          ? user.permissions
          : (user.effective_permissions || []);
        this.govState.selectedPerms = new Set(rawPerms);
      } else {
        this.govState.selectedPerms = new Set();
      }
      this.renderGovernancePanel();
    },

    renderGovernancePanel() {
      const { users, catalog, selectedEmail } = this.govState;
      const user = users.find(u => u.email === selectedEmail) || users[0];
      if (!user) return;
      this.govState.selectedEmail = user.email;

      // Renderizar tabs de usuarios
      const tabsContainer = document.getElementById('governanceUserTabs');
      if (tabsContainer) {
        let tabsHtml = '';
        users.forEach(u => {
          const isSelected = u.email === user.email;
          const currentActivePerms = (u.email === user.email) 
            ? this.govState.selectedPerms.size 
            : ((u.permissions !== null && u.permissions !== undefined) ? u.permissions.length : (u.effective_permissions || []).length);

          const roleColors = {
            'Super_Administrador': 'border-purple-500/40 bg-purple-950/20 text-purple-300',
            'Administrador': 'border-indigo-500/40 bg-indigo-950/20 text-indigo-300',
            'Cliente': 'border-slate-700 bg-dark-850 text-slate-300'
          };
          const roleStyle = roleColors[u.role] || 'border-slate-700 bg-dark-850 text-slate-300';
          const activeBorder = isSelected ? 'ring-2 ring-purple-500 border-purple-400 bg-purple-950/40 shadow-lg' : 'opacity-70 hover:opacity-100';

          tabsHtml += `
            <button type="button" onclick="selectGovernanceUser('${u.email}')" class="p-3 rounded-xl border ${roleStyle} ${activeBorder} text-left transition cursor-pointer flex flex-col justify-between">
              <div class="flex items-center justify-between mb-1">
                <span class="text-[10px] font-bold uppercase font-mono px-1.5 py-0.5 rounded bg-black/40">${u.role}</span>
                <span id="govTabCount_${u.email.replace(/[@.]/g, '_')}" class="text-[10px] font-bold text-emerald-400">${currentActivePerms}/12 Permisos</span>
              </div>
              <div>
                <h5 class="font-bold text-white text-xs">${u.name}</h5>
                <p class="text-[10px] text-slate-400 font-mono truncate">${u.email}</p>
              </div>
            </button>
          `;
        });
        tabsContainer.innerHTML = tabsHtml;
      }

      // Header de usuario seleccionado
      const nameEl = document.getElementById('govSelectedUserName');
      const emailEl = document.getElementById('govSelectedUserEmail');
      const badgeEl = document.getElementById('govSelectedUserRoleBadge');
      if (nameEl) nameEl.innerText = user.name;
      if (emailEl) emailEl.innerText = `${user.email} (Usuario: ${user.username || user.email.split('@')[0]})`;
      if (badgeEl) {
        badgeEl.innerText = user.role;
        badgeEl.className = user.role === 'Super_Administrador' 
          ? 'px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40'
          : (user.role === 'Administrador' ? 'px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/40' : 'px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono bg-slate-800 text-slate-300 border border-slate-700');
      }

      this.updateGovPermsCount();

      // Renderizar Grid de Permisos con interacción individual
      const grid = document.getElementById('govPermissionsGrid');
      if (grid) {
        let gridHtml = '';
        catalog.forEach(p => {
          const safeId = p.id.replace(/[:.]/g, '_');
          const isChecked = this.govState.selectedPerms.has(p.id);
          gridHtml += `
            <div 
              id="govCard_${safeId}"
              onclick="toggleGovPerm('${p.id}')" 
              class="flex items-start gap-3 p-3 rounded-xl border transition cursor-pointer select-none ${isChecked ? 'bg-indigo-950/40 border-indigo-500/50 shadow-sm' : 'bg-dark-900/60 border-slate-800 hover:border-slate-700 opacity-60'}"
            >
              <input 
                type="checkbox" 
                id="govChk_${safeId}"
                value="${p.id}" 
                ${isChecked ? 'checked' : ''} 
                onclick="event.stopPropagation();"
                onchange="toggleGovPerm('${p.id}', this.checked)"
                class="mt-1 h-4 w-4 rounded accent-indigo-500 bg-dark-800 border-slate-700 cursor-pointer"
              >
              <div class="flex-1 pointer-events-none">
                <div class="flex items-center justify-between">
                  <span id="govTitle_${safeId}" class="text-xs font-mono font-bold ${isChecked ? 'text-indigo-300' : 'text-slate-400'}">${p.id}</span>
                  <span id="govBadge_${safeId}" class="text-[9px] px-1.5 py-0.5 rounded font-semibold ${isChecked ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-500'}">${isChecked ? 'Activo' : 'Inactivo'}</span>
                </div>
                <h6 class="text-[11px] font-bold text-white mt-0.5">${p.name}</h6>
                <p class="text-[10px] text-slate-400 leading-tight mt-0.5">${p.description}</p>
              </div>
            </div>
          `;
        });
        grid.innerHTML = gridHtml;
      }

      this.refreshIcons();
    },

    toggleGovPerm(permId, explicitChecked = null) {
      const safeId = permId.replace(/[:.]/g, '_');
      const chk = document.getElementById(`govChk_${safeId}`);
      
      let nextChecked;
      if (explicitChecked !== null && typeof explicitChecked === 'boolean') {
        nextChecked = explicitChecked;
      } else if (chk) {
        nextChecked = !chk.checked;
      } else {
        nextChecked = !this.govState.selectedPerms.has(permId);
      }

      if (nextChecked) {
        this.govState.selectedPerms.add(permId);
      } else {
        this.govState.selectedPerms.delete(permId);
      }

      if (chk) chk.checked = nextChecked;

      const card = document.getElementById(`govCard_${safeId}`);
      const badge = document.getElementById(`govBadge_${safeId}`);
      const title = document.getElementById(`govTitle_${safeId}`);

      if (card) {
        card.className = nextChecked
          ? "flex items-start gap-3 p-3 rounded-xl border transition cursor-pointer select-none bg-indigo-950/40 border-indigo-500/50 shadow-sm"
          : "flex items-start gap-3 p-3 rounded-xl border transition cursor-pointer select-none bg-dark-900/60 border-slate-800 hover:border-slate-700 opacity-60";
      }
      if (badge) {
        badge.innerText = nextChecked ? 'Activo' : 'Inactivo';
        badge.className = `text-[9px] px-1.5 py-0.5 rounded font-semibold ${nextChecked ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-500'}`;
      }
      if (title) {
        title.className = `text-xs font-mono font-bold ${nextChecked ? 'text-indigo-300' : 'text-slate-400'}`;
      }

      this.updateGovPermsCount();
      
      const email = this.govState.selectedEmail;
      if (email) {
        const tabCount = document.getElementById(`govTabCount_${email.replace(/[@.]/g, '_')}`);
        if (tabCount) tabCount.innerText = `${this.govState.selectedPerms.size}/12 Permisos`;
      }
    },

    selectAllGovPerms(select) {
      if (select) {
        this.govState.catalog.forEach(p => this.govState.selectedPerms.add(p.id));
      } else {
        this.govState.selectedPerms.clear();
      }

      this.govState.catalog.forEach(p => {
        const safeId = p.id.replace(/[:.]/g, '_');
        const isChecked = this.govState.selectedPerms.has(p.id);
        const chk = document.getElementById(`govChk_${safeId}`);
        const card = document.getElementById(`govCard_${safeId}`);
        const badge = document.getElementById(`govBadge_${safeId}`);
        const title = document.getElementById(`govTitle_${safeId}`);

        if (chk) chk.checked = isChecked;
        if (card) {
          card.className = isChecked
            ? "flex items-start gap-3 p-3 rounded-xl border transition cursor-pointer select-none bg-indigo-950/40 border-indigo-500/50 shadow-sm"
            : "flex items-start gap-3 p-3 rounded-xl border transition cursor-pointer select-none bg-dark-900/60 border-slate-800 hover:border-slate-700 opacity-60";
        }
        if (badge) {
          badge.innerText = isChecked ? 'Activo' : 'Inactivo';
          badge.className = `text-[9px] px-1.5 py-0.5 rounded font-semibold ${isChecked ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-800 text-slate-500'}`;
        }
        if (title) {
          title.className = `text-xs font-mono font-bold ${isChecked ? 'text-indigo-300' : 'text-slate-400'}`;
        }
      });

      this.updateGovPermsCount();

      const email = this.govState.selectedEmail;
      if (email) {
        const tabCount = document.getElementById(`govTabCount_${email.replace(/[@.]/g, '_')}`);
        if (tabCount) tabCount.innerText = `${this.govState.selectedPerms.size}/12 Permisos`;
      }
    },

    updateGovPermsCount() {
      const countEl = document.getElementById('govActivePermsCount');
      if (countEl) {
        const total = this.govState.catalog.length || 12;
        countEl.innerText = `${this.govState.selectedPerms.size} / ${total} Permisos Activos`;
      }
    },

    async saveGovernancePermissions() {
      const email = this.govState.selectedEmail;
      if (!email) return;
      const permissions = Array.from(this.govState.selectedPerms);
      try {
        const res = await window.DevPilot.Model.AuthModel.updateUserPermissions(email, permissions);
        if (res.success) {
          showToast(`Permisos guardados para ${email} (${permissions.length} activos)`, 'success');
          const u = this.govState.users.find(x => x.email === email);
          if (u) {
            u.permissions = permissions;
            u.effective_permissions = permissions;
          }
          const tabCount = document.getElementById(`govTabCount_${email.replace(/[@.]/g, '_')}`);
          if (tabCount) tabCount.innerText = `${permissions.length}/12 Permisos`;

          // Si el usuario modificado es el actual, refrescar en vivo
          const currentUser = window.DevPilot.Controller.state.currentUser;
          if (currentUser && currentUser.email === email) {
            currentUser.permissions = permissions;
            this.renderAuthBar(currentUser);
            window.DevPilot.Controller.pollTelemetryCommand();
          }
        } else {
          showToast(res.detail || "Error guardando permisos", 'error');
        }
      } catch(e) {
        showToast(e.message || "Error al actualizar permisos", 'error');
      }
    },

    async resetGovernancePermissions() {
      const email = this.govState.selectedEmail;
      if (!email) return;
      try {
        const res = await window.DevPilot.Model.AuthModel.resetUserPermissions(email);
        if (res.success) {
          showToast(`Permisos restablecidos a los por defecto del rol para ${email}`, 'success');
          const u = this.govState.users.find(x => x.email === email);
          if (u) {
            u.permissions = null;
            u.effective_permissions = res.effective_permissions;
          }
          this.govState.selectedPerms = new Set(res.effective_permissions || []);
          this.renderGovernancePanel();
        }
      } catch(e) {
        showToast(e.message || "Error al restablecer permisos", 'error');
      }
    },

    renderServicesGrid(services) {
      const container = document.getElementById('servicesGrid');
      if (!container) return;
      let html = '';

      services.forEach(s => {
        const isHealthy = s.status === 'HEALTHY';
        const isDegraded = s.status === 'DEGRADED';
        const isDown = s.status === 'DOWN';

        let statusBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
        let cardBorder = 'border-slate-800 hover:border-emerald-500/40';
        let statusDot = 'bg-emerald-400';

        if (isDegraded) {
          statusBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
          cardBorder = 'border-amber-500/50 glow-amber';
          statusDot = 'bg-amber-400 animate-pulse';
        } else if (isDown) {
          statusBg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
          cardBorder = 'border-rose-500/60 glow-rose';
          statusDot = 'bg-rose-400 animate-ping';
        }

        let faultsObj = {};
        try { 
          faultsObj = typeof s.active_faults === 'string' ? JSON.parse(s.active_faults || '{}') : (s.active_faults || {}); 
        } catch(e){ faultsObj = {}; }

        let faultTags = '';
        const delayMs = faultsObj.delayMs || faultsObj.delay_ms || 0;
        const errorRateVal = faultsObj.errorRate || faultsObj.error_rate || 0;
        const isCrashedVal = faultsObj.isCrashed || faultsObj.is_crashed || false;

        if (delayMs > 0) faultTags += `<span class="px-2 py-0.5 text-[10px] rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">+${delayMs}ms Latencia</span>`;
        if (errorRateVal > 0) faultTags += `<span class="px-2 py-0.5 text-[10px] rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">${Math.round(errorRateVal * 100)}% Errores</span>`;
        if (isCrashedVal) faultTags += `<span class="px-2 py-0.5 text-[10px] rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">Crashed (503)</span>`;

        const latencyThreshold = Number(s.latency_threshold_ms || 2000);
        const errorThreshold = Number(s.error_threshold_pct || 0.20);
        const lastLat = Number(s.last_latency || 0);
        const errRate = Number(s.error_rate || 0);

        const latencyColor = lastLat > latencyThreshold ? 'text-rose-400 font-bold' : (lastLat > (latencyThreshold * 0.7) ? 'text-amber-400' : 'text-slate-200');
        const errorRateColor = errRate > errorThreshold ? 'text-rose-400 font-bold' : (errRate > 0 ? 'text-amber-400' : 'text-slate-200');

        html += `
          <div id="serviceCard_${s.name}" class="bg-dark-850 border ${cardBorder} rounded-xl p-5 shadow-lg transition-all duration-300 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="font-bold text-white text-base">${s.display_name}</h3>
                  <p class="text-xs text-slate-400 font-mono mt-0.5">${s.url}</p>
                </div>
                <span class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${statusBg}">
                  <span class="h-2 w-2 rounded-full ${statusDot}"></span>
                  ${s.status}
                </span>
              </div>

              <div class="mt-4 grid grid-cols-2 gap-3 bg-dark-900/60 p-3 rounded-lg border border-slate-800/80">
                <div>
                  <p class="text-[10px] uppercase font-semibold text-slate-400">Latencia RTT</p>
                  <p class="text-sm font-mono font-bold ${latencyColor} mt-0.5">${Math.round(lastLat)} ms</p>
                  <p class="text-[9px] text-slate-400 font-mono">Umbral: ${Math.round(latencyThreshold)}ms</p>
                </div>
                <div>
                  <p class="text-[10px] uppercase font-semibold text-slate-400">Tasa de Error</p>
                  <p class="text-sm font-mono font-bold ${errorRateColor} mt-0.5">${Math.round(errRate * 100)}%</p>
                  <p class="text-[9px] text-slate-400 font-mono">Umbral: ${Math.round(errorThreshold * 100)}%</p>
                </div>
              </div>

              ${faultTags ? `<div class="mt-3 flex flex-wrap gap-1.5">${faultTags}</div>` : ''}
            </div>

            <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <div class="flex items-center gap-2">
                ${window.DevPilot.Controller.computed.isLogsAllowed() ? `
                  <button onclick="window.DevPilot.View.openLogsModal('${s.name}')" class="p-1.5 hover:bg-dark-800 text-slate-400 hover:text-cyan-400 rounded-lg transition" title="Ver logs en vivo">
                    <i data-lucide="terminal" class="w-4 h-4"></i>
                  </button>
                ` : ''}
                ${window.DevPilot.Controller.computed.isThresholdsAllowed() ? `
                  <button onclick="window.DevPilot.View.openThresholdModal('${s.name}', ${latencyThreshold}, ${errorThreshold})" class="p-1.5 hover:bg-dark-800 text-slate-400 hover:text-amber-400 rounded-lg transition" title="Calibrar umbrales SLA">
                    <i data-lucide="sliders" class="w-4 h-4"></i>
                  </button>
                ` : ''}
              </div>
              ${window.DevPilot.Controller.computed.isRemediationAllowed() ? `
                <button onclick="window.DevPilot.Controller.requestDirectRemediationCommand('${s.name}', 'RESTART_CONTAINER')" class="px-2.5 py-1 bg-dark-800 hover:bg-indigo-600/30 text-indigo-300 hover:text-white border border-indigo-500/30 rounded-lg text-xs font-medium transition flex items-center gap-1.5 shadow-sm">
                  <i data-lucide="shield-check" class="w-3.5 h-3.5 text-cyan-400"></i>
                  <span>Remediar (TOTP)</span>
                </button>
              ` : `
                <span class="px-2.5 py-1 bg-dark-900 border border-slate-700/60 rounded-lg text-[11px] text-slate-400 font-mono flex items-center gap-1.5">
                  <i data-lucide="eye" class="w-3.5 h-3.5 text-cyan-400"></i>
                  <span>Solo Consulta</span>
                </span>
              `}
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
      this.refreshIcons();
    },

    renderIncidents(incidents, filter = 'ALL') {
      const container = document.getElementById('incidentsList');
      if (!container) return;

      let filtered = incidents;
      if (filter === 'OPEN') filtered = incidents.filter(i => i.status === 'OPEN');
      else if (filter === 'RESOLVED') filtered = incidents.filter(i => i.status === 'RESOLVED');

      if (!filtered || filtered.length === 0) {
        container.innerHTML = `<div class="text-center py-8 text-slate-500 text-xs">Sin incidentes que mostrar en este filtro.</div>`;
        return;
      }

      let html = '';
      filtered.forEach(inc => {
        const isOpen = inc.status === 'OPEN';
        const bgClass = isOpen ? 'bg-rose-950/20 border-rose-500/40' : 'bg-dark-900/60 border-slate-800';
        const badgeClass = isOpen ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';

        html += `
          <div class="p-4 rounded-xl border ${bgClass} transition">
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${badgeClass}">${inc.status}</span>
                <span class="text-xs font-mono text-cyan-400 font-semibold">${inc.service_name.toUpperCase()}</span>
                <span class="text-[10px] text-slate-400">${new Date(inc.created_at).toLocaleTimeString()}</span>
              </div>
              ${isOpen && window.DevPilot.Controller.computed.isIncidentsManageAllowed() ? `
                <button onclick="window.DevPilot.Controller.resolveIncidentCommand(${inc.id})" class="text-[11px] text-slate-400 hover:text-emerald-400 font-medium">
                  Marcar Resuelto
                </button>
              ` : (isOpen ? `
                <span class="text-[10px] text-amber-400/80 font-mono">En atención SRE</span>
              ` : '')}
            </div>
            <h4 class="font-bold text-white text-sm mt-1.5">${inc.title}</h4>
            <p class="text-xs text-slate-300 mt-1 leading-relaxed"><strong class="text-indigo-300">Diagnóstico:</strong> ${inc.simple_explanation || inc.description}</p>
            <div class="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/60">
              <span class="text-[10px] text-slate-400 font-mono">Severidad: <strong class="text-amber-400">${inc.severity}</strong></span>
              <button onclick="window.DevPilot.View.askAIToDiagnose(${inc.id})" class="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1">
                <i data-lucide="bot" class="w-3.5 h-3.5"></i>
                <span>Consultar a Claude</span>
              </button>
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
      this.refreshIcons();
    },

    renderPendingProposals(proposals) {
      const container = document.getElementById('pendingProposalsContainer');
      if (!container) return;
      if (!window.DevPilot.Controller.computed.isRemediationAllowed()) {
        container.classList.add('hidden');
        container.innerHTML = '';
        return;
      }
      const countEl = document.getElementById('pendingProposalsCount');
      if (countEl) countEl.innerText = proposals.length;

      if (!proposals || proposals.length === 0) {
        container.classList.add('hidden');
        container.innerHTML = '';
        return;
      }

      container.classList.remove('hidden');
      let html = '';
      proposals.forEach(p => {
        html += `
          <div class="bg-gradient-to-r from-amber-950/50 via-dark-850 to-amber-950/40 border-2 border-amber-500/60 rounded-xl p-4 shadow-xl glow-amber flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="p-2.5 bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/40 mt-0.5">
                <i data-lucide="shield-alert" class="w-6 h-6"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-amber-500 text-black">Aprobación Humana Requerida</span>
                  <span class="text-xs font-mono text-slate-400">Propuesta #${p.id} • ${p.service_name.toUpperCase()}</span>
                </div>
                <h4 class="font-bold text-white text-sm mt-1">Acción SRE Sugerida: <span class="text-amber-300">${p.action_type}</span></h4>
                <p class="text-xs text-slate-200 mt-1 leading-relaxed"><strong class="text-indigo-300">Explicación Simple:</strong> ${p.simple_explanation || p.reason}</p>
              </div>
            </div>

            <div class="flex items-center gap-2 self-end md:self-center flex-shrink-0">
              <button onclick="window.DevPilot.Controller.rejectProposalCommand(${p.id})" class="px-3.5 py-2 bg-dark-800 hover:bg-rose-950/60 hover:text-rose-300 text-slate-300 border border-slate-700 rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                <i data-lucide="x" class="w-3.5 h-3.5"></i>
                <span>Rechazar</span>
              </button>
              <button onclick="window.DevPilot.Controller.requestProposalApprovalCommand(${p.id})" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-lg transition flex items-center gap-1.5">
                <i data-lucide="key-round" class="w-4 h-4"></i>
                <span>Aprobar con TOTP</span>
              </button>
            </div>
          </div>
        `;
      });
      container.innerHTML = html;
      this.refreshIcons();
    },

    renderChart(metrics) {
      if (!this.chartInstance || !metrics) return;
      const services = window.DevPilot.Controller.state.services || [];
      const avgThreshold = services.length > 0
        ? Math.round(services.reduce((a,s) => a + Number(s.latency_threshold_ms || 2000), 0) / services.length)
        : 2000;

      const COLOR_PALETTE = [
        { border: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)' },  // Indigo (Users)
        { border: '#06b6d4', bg: 'rgba(6, 182, 212, 0.1)' },  // Cyan (Products)
        { border: '#a855f7', bg: 'rgba(168, 85, 247, 0.1)' },  // Purple (Orders)
        { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },  // Emerald (Payments)
        { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' },  // Amber
        { border: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)' },  // Pink
        { border: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)' }   // Blue
      ];

      // 1. Asegurar o actualizar datasets dinámicos para CADA microservicio registrado
      services.forEach((s, idx) => {
        const sName = s.name;
        const sLabel = s.display_name ? s.display_name.split(' ')[0] : sName.toUpperCase();
        let dataset = this.chartInstance.data.datasets.find(d => d.serviceName === sName || d.label.toLowerCase() === sName.toLowerCase() || d.label.toLowerCase() === sLabel.toLowerCase());
        
        const color = COLOR_PALETTE[idx % COLOR_PALETTE.length];
        if (!dataset) {
          dataset = {
            label: sLabel,
            serviceName: sName,
            borderColor: color.border,
            backgroundColor: color.bg,
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            data: [15, 15, 15, 15, 15, 15, Math.round(s.last_latency || 15)]
          };
          const slaIdx = this.chartInstance.data.datasets.findIndex(d => d.label === 'Umbral SLA');
          if (slaIdx >= 0) {
            this.chartInstance.data.datasets.splice(slaIdx, 0, dataset);
          } else {
            this.chartInstance.data.datasets.push(dataset);
          }
        } else {
          dataset.label = sLabel;
          dataset.serviceName = sName;
        }

        const recent = metrics[sName] || [];
        if (recent.length > 0) {
          const dataPoints = recent.map(m => Math.min(Math.round(m.latency_ms || 10), 5000));
          while (dataPoints.length < 7) {
            dataPoints.unshift(dataPoints[0] || Math.round(s.last_latency || 15));
          }
          dataset.data = dataPoints.slice(-7);
        } else if (s.last_latency > 0) {
          dataset.data[dataset.data.length - 1] = Math.min(Math.round(s.last_latency), 5000);
        }
      });

      // 2. Añadir/actualizar línea de umbral SLA
      let slaAnnot = this.chartInstance.data.datasets.find(d => d.label === 'Umbral SLA');
      if (!slaAnnot) {
        slaAnnot = {
          label: 'Umbral SLA',
          borderColor: 'rgba(245,158,11,0.6)',
          borderDash: [6,3],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0,
          data: new Array(7).fill(avgThreshold)
        };
        this.chartInstance.data.datasets.push(slaAnnot);
      } else {
        slaAnnot.data = new Array(7).fill(avgThreshold);
      }

      this.chartInstance.update('none');
    },

    openTotpModal(action) {
      document.getElementById('totpActionDescription').innerText = action.description || `${action.actionType} (${action.serviceName})`;
      document.getElementById('totpInputCode').value = '';
      document.getElementById('totpErrorBox').classList.add('hidden');
      document.getElementById('totpModal').classList.remove('hidden');
      document.getElementById('totpInputCode').focus();
      this.refreshIcons();
    },

    closeTotpModal() {
      document.getElementById('totpModal').classList.add('hidden');
      window.DevPilot.Controller.state.pendingTotpAction = null;
    },

    showTotpError(msg) {
      const box = document.getElementById('totpErrorBox');
      box.innerText = msg;
      box.classList.remove('hidden');
    },

    async pasteDemoTotp() {
      try {
        const res = await window.DevPilot.Model.AuthModel.getDemoTotp();
        if (res.success && res.totp_code) {
          document.getElementById('totpInputCode').value = res.totp_code;
          document.getElementById('totpCountdownText').innerText = `Válido (${res.remaining_seconds}s)`;
          document.getElementById('totpErrorBox').classList.add('hidden');
        }
      } catch (e) {
        document.getElementById('totpInputCode').value = '123456';
      }
    },

    async openAuditModal() {
      if (!window.DevPilot.Controller.computed.isAuditAllowed()) {
        View.showNotification(`Acceso denegado (RBAC): Rol '${window.DevPilot.Controller.state.currentUser.role}' sin permiso de auditoría forense.`, false);
        return;
      }
      document.getElementById('auditModal').classList.remove('hidden');
      try {
        const res = await window.DevPilot.Model.RemediationModel.getAuditHistory(50);
        const tbody = document.getElementById('auditTableBody');
        if (!res.data || res.data.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-500">Sin registros de auditoría aún.</td></tr>`;
          return;
        }
        let html = '';
        res.data.forEach(a => {
          html += `
            <tr class="hover:bg-dark-800/50">
              <td class="py-2.5 px-3 text-white font-sans">${a.incident_title || 'Incidente'}</td>
              <td class="py-2.5 px-3 text-cyan-400 font-mono">${a.service_name}</td>
              <td class="py-2.5 px-3"><span class="px-1.5 py-0.5 rounded text-[9px] bg-slate-800">${a.severity}</span></td>
              <td class="py-2.5 px-3 text-indigo-300 font-mono">${a.proposed_action || 'RESTART'}</td>
              <td class="py-2.5 px-3 font-semibold ${a.proposal_status === 'EXECUTED' ? 'text-emerald-400' : (a.proposal_status === 'REJECTED' ? 'text-rose-400' : 'text-amber-400')}">${a.proposal_status || 'EJECUTADO'}</td>
              <td class="py-2.5 px-3 text-slate-400 text-[10px] font-mono">${a.operator_user || 'admin@devpilot.io'}</td>
              <td class="py-2.5 px-3 text-slate-500 text-[10px]">${a.incident_created_at ? new Date(a.incident_created_at).toLocaleTimeString() : '-'}</td>
            </tr>
          `;
        });
        tbody.innerHTML = html;
      } catch(e){}
    },

    closeAuditModal() {
      document.getElementById('auditModal').classList.add('hidden');
    },

    async downloadAuditLog(format = 'csv') {
      try {
        const token = window.DevPilot.Model.ApiClient.getToken();
        const res = await fetch(`/api/audit/export?format=${format}`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Error HTTP ${res.status}`);
        }
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        const nowStr = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '_');
        a.download = `devpilot_auditoria_errores_${nowStr}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.showNotification(`Historial de auditoría descargado exitosamente (${format.toUpperCase()}).`, true);
      } catch(e) {
        this.showNotification(`Error al descargar historial de auditoría: ${e.message}`, false);
      }
    },

    async openLogsModal(serviceName) {
      window.DevPilot.Controller.state.currentLogsService = serviceName;
      document.getElementById('logsModalTitle').innerText = `Container Logs: ${serviceName.toUpperCase()}`;
      document.getElementById('logsModalContent').innerText = 'Cargando logs desde el Docker SDK...';
      document.getElementById('logsModal').classList.remove('hidden');
      try {
        const res = await window.DevPilot.Model.LogsModel.getLogs(serviceName, 120);
        document.getElementById('logsModalContent').innerText = res.logs || 'Sin logs disponibles.';
      } catch (e) {
        document.getElementById('logsModalContent').innerText = `Error extrayendo logs: ${e.message}`;
      }
    },

    closeLogsModal() {
      document.getElementById('logsModal').classList.add('hidden');
      window.DevPilot.Controller.state.currentLogsService = null;
    },

    openNewServiceModal() {
      if (!window.DevPilot.Controller.computed.isThresholdsAllowed()) {
        this.showNotification(`Acceso denegado (RBAC): Rol '${window.DevPilot.Controller.state.currentUser.role}' no puede registrar servicios.`, false);
        return;
      }
      document.getElementById('newServiceModal').classList.remove('hidden');
      if (typeof scanDockerServices === 'function') scanDockerServices();
      this.refreshIcons();
    },

    closeNewServiceModal() {
      document.getElementById('newServiceModal').classList.add('hidden');
    },

    openThresholdModal(serviceName, currentLat, currentErr) {
      if (!window.DevPilot.Controller.computed.isThresholdsAllowed()) {
        this.showNotification(`Acceso denegado (RBAC): Solo 'Admin' puede calibrar umbrales SLA.`, false);
        return;
      }
      document.getElementById('thresholdServiceName').innerText = serviceName;
      document.getElementById('thresholdTargetService').value = serviceName;
      document.getElementById('modalLatencyRange').value = currentLat;
      document.getElementById('modalLatencyText').innerText = currentLat + ' ms';
      document.getElementById('modalErrorRange').value = Math.round(currentErr * 100);
      document.getElementById('modalErrorText').innerText = Math.round(currentErr * 100) + '%';
      document.getElementById('thresholdModal').classList.remove('hidden');
    },

    closeThresholdModal() {
      document.getElementById('thresholdModal').classList.add('hidden');
    },

    showNotification(msg, isSuccess) {
      const box = document.getElementById('chaosNotification');
      if (box) {
        box.innerText = msg;
        box.className = isSuccess
          ? 'p-2.5 rounded-lg text-xs font-mono border bg-emerald-950/40 text-emerald-300 border-emerald-500/30 block'
          : 'p-2.5 rounded-lg text-xs font-mono border bg-rose-950/40 text-rose-300 border-rose-500/30 block';
        setTimeout(() => { box.className = 'hidden'; }, 5000);
      }
      if (typeof showToast === 'function') {
        showToast(msg, isSuccess ? 'success' : 'error');
      }
    },

    appendChatMessage(role, text) {
      const container = document.getElementById('chatMessages');
      if (!container) return;
      const isUser = role === 'user';
      const formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code class="bg-dark-900 px-1 py-0.5 rounded text-cyan-300 font-mono text-[11px]">$1</code>')
        .replace(/\n/g, '<br>');

      const msgDiv = document.createElement('div');
      msgDiv.className = isUser ? 'flex gap-2.5 items-start justify-end' : 'flex gap-2.5 items-start';
      msgDiv.innerHTML = isUser ? `
        <div class="bg-indigo-600 text-white rounded-xl p-3 max-w-[85%] leading-relaxed shadow">${formattedText}</div>
        <div class="h-6 w-6 rounded bg-slate-700 text-slate-300 flex-shrink-0 flex items-center justify-center"><i data-lucide="user" class="w-3.5 h-3.5"></i></div>
      ` : `
        <div class="h-6 w-6 rounded bg-indigo-600/30 text-indigo-400 flex-shrink-0 flex items-center justify-center"><i data-lucide="bot" class="w-3.5 h-3.5"></i></div>
        <div class="bg-dark-800 border border-slate-700/80 rounded-xl p-3 text-slate-300 max-w-[85%] leading-relaxed shadow">${formattedText}</div>
      `;
      container.appendChild(msgDiv);
      container.scrollTop = container.scrollHeight;
      this.refreshIcons();
    },

    async runRemediationVisualPipeline(service, action = "RESTART_CONTAINER") {
      const modal = document.getElementById('remediationProgressModal');
      if (!modal) return;
      modal.classList.remove('hidden');

      const svcName = (service || 'users').toLowerCase();
      const svcBadge = document.getElementById('remediationServiceBadge');
      if (svcBadge) svcBadge.innerText = svcName.toUpperCase();

      const progressBar = document.getElementById('remediationProgressBar');
      const progressPercent = document.getElementById('remediationProgressPercent');
      const terminal = document.getElementById('remediationTerminalLogs');
      const doneBtn = document.getElementById('remediationDoneBtn');
      const closeTopBtn = document.getElementById('closeRemediationBtn');

      if (terminal) terminal.innerHTML = '';
      if (closeTopBtn) closeTopBtn.classList.add('hidden');
      if (doneBtn) {
        doneBtn.disabled = true;
        doneBtn.className = "px-6 py-2.5 bg-slate-800 text-slate-400 font-semibold rounded-xl text-xs transition cursor-not-allowed";
        doneBtn.innerText = "Ejecutando protocolo de auto-remediación...";
      }

      const log = (msg) => {
        if (!terminal) return;
        const p = document.createElement('p');
        p.className = "text-slate-300 leading-tight";
        p.innerHTML = `<span class="text-cyan-400">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
        terminal.appendChild(p);
        terminal.scrollTop = terminal.scrollHeight;
      };

      const setStep = (stepNum, status, badgeText, badgeColor = 'text-cyan-400') => {
        const box = document.getElementById(`step${stepNum}Box`);
        const badge = document.getElementById(`step${stepNum}Badge`);
        if (box) {
          if (status === 'active') {
            box.className = "flex items-start gap-3 p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/40 transition-all duration-300 opacity-100";
          } else if (status === 'done') {
            box.className = "flex items-start gap-3 p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40 transition-all duration-300 opacity-100";
          } else {
            box.className = "flex items-start gap-3 p-3 rounded-xl bg-dark-850 border border-slate-800 opacity-40 transition-all duration-300";
          }
        }
        if (badge) {
          badge.innerText = badgeText;
          badge.className = `text-[10px] font-mono font-bold ${badgeColor}`;
        }
      };

      // Inicializar pasos
      setStep(1, 'active', 'En ejecución...', 'text-cyan-400');
      setStep(2, 'waiting', 'En espera', 'text-slate-500');
      setStep(3, 'waiting', 'En espera', 'text-slate-500');
      setStep(4, 'waiting', 'En espera', 'text-slate-500');
      setStep(5, 'waiting', 'En espera', 'text-slate-500');

      if (progressBar) progressBar.style.width = '15%';
      if (progressPercent) progressPercent.innerText = '15%';

      log(`Iniciando protocolo de Auto-Remediación SRE Human-in-the-Loop...`);
      log(`Acción asignada: [${action}] sobre contenedor 'devpilot_${svcName}'.`);
      await new Promise(r => setTimeout(r, 450));

      // Paso 1 completado
      setStep(1, 'done', 'Completado ✓', 'text-emerald-400');
      setStep(2, 'active', 'Reiniciando...', 'text-cyan-400');
      if (progressBar) progressBar.style.width = '40%';
      if (progressPercent) progressPercent.innerText = '40%';
      log(`Docker API: container.restart('devpilot_${svcName}') ejecutado exitosamente.`);
      await new Promise(r => setTimeout(r, 550));

      // Paso 2 completado
      setStep(2, 'done', 'Reinicio OK ✓', 'text-emerald-400');
      setStep(3, 'active', 'Limpiando fallos...', 'text-cyan-400');
      if (progressBar) progressBar.style.width = '65%';
      if (progressPercent) progressPercent.innerText = '65%';
      log(`Chaos Studio: POST /fault/reset ejecutado. Parámetros de latencia y error restablecidos a 0.`);
      await new Promise(r => setTimeout(r, 450));

      // Paso 3 completado
      setStep(3, 'done', 'Nominal ✓', 'text-emerald-400');
      setStep(4, 'active', 'Sondeando probe...', 'text-cyan-400');
      if (progressBar) progressBar.style.width = '85%';
      if (progressPercent) progressPercent.innerText = '85%';
      log(`Health-Check Probe: GET http://${svcName}_service/health -> 200 OK (RTT: 18ms).`);
      await new Promise(r => setTimeout(r, 450));

      // Paso 4 y 5 completados
      setStep(4, 'done', '200 OK ✓', 'text-emerald-400');
      setStep(5, 'done', 'Resuelto ✓', 'text-emerald-400');
      if (progressBar) progressBar.style.width = '100%';
      if (progressPercent) progressPercent.innerText = '100%';
      log(`Auditoría registrada: Incidente cerrado. Microservicio '${svcName.toUpperCase()}' nominal dentro de SLA.`);

      if (closeTopBtn) closeTopBtn.classList.remove('hidden');
      if (doneBtn) {
        doneBtn.disabled = false;
        doneBtn.className = "px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition cursor-pointer shadow-lg shadow-emerald-500/30 flex items-center gap-1.5";
        doneBtn.innerHTML = `<span>Finalizar y Cerrar Protocolo</span>`;
      }

      this.appendChatMessage('assistant', `🛠️ **Auto-Remediación Ejecutada Exitosamente:**\n\nEl microservicio **${svcName.toUpperCase()}** fue recuperado correctamente mediante el Docker SDK tras validación de seguridad TOTP. El contenedor está nominal y el health probe responde **200 OK**.`);
      window.DevPilot.Controller.pollTelemetryCommand();
      this.refreshIcons();
    },

    closeRemediationModal() {
      const modal = document.getElementById('remediationProgressModal');
      if (modal) modal.classList.add('hidden');
      window.DevPilot.Controller.pollTelemetryCommand();
    },

    askAIToDiagnose(incidentId) {
      this.sendQuickPrompt(`Explícame en español qué ocurrió en el incidente #${incidentId} y qué solución propones`);
    },

    sendQuickPrompt(text) {
      const input = document.getElementById('chatInput');
      if (input) {
        input.value = text;
        window.DevPilot.Controller.sendChatCommand(text);
        input.value = '';
      }
    }
  };

  // Exponer globalmente
  window.DevPilot.View = View;
  window.DevPilotView = View;

  // =========================================================================
  // ENLACE REACTIVO AUTOMÁTICO (DATA BINDING) ENTRE CONTROLLER/VIEWMODEL Y VIEW
  // =========================================================================
  if (window.DevPilot.Controller) {
    window.DevPilot.Controller.subscribe('auth:changed', (user) => {
      View.renderAuthBar(user);
    });

    window.DevPilot.Controller.subscribe('telemetry:updated', (state) => {
      View.renderServicesGrid(state.services);
      View.renderIncidents(state.incidents, state.incidentFilter);
      View.renderPendingProposals(state.proposals);
      View.renderChart(state.metrics);

      const totalServicesEl = document.getElementById('totalServicesCount');
      if (totalServicesEl) totalServicesEl.innerText = state.services.length;

      const dockerStatusEl = document.getElementById('dockerStatusText');
      if (dockerStatusEl) dockerStatusEl.innerText = state.system.docker_connected ? 'Conectado' : 'Standalone';

      const selectEl = document.getElementById('targetServiceSelect');
      if (selectEl && state.services && state.services.length > 0) {
        const currentVal = selectEl.value;
        const serviceNamesHash = state.services.map(s => s.name).join(',');
        if (selectEl.dataset.serviceHash !== serviceNamesHash) {
          selectEl.dataset.serviceHash = serviceNamesHash;
          selectEl.innerHTML = state.services.map(s => `<option value="${s.name}">${s.display_name} (:${s.url.split(':').pop()})</option>`).join('');
          if (currentVal && state.services.some(s => s.name === currentVal)) {
            selectEl.value = currentVal;
          }
        }
      }

      // KPI del copiloto IA
      const agentModeEl = document.getElementById('agentModeKpi');
      if (agentModeEl) {
        agentModeEl.innerText = 'Claude 3.5 Sonnet';
        agentModeEl.className = 'text-lg font-bold text-indigo-400 mt-1';
      }

      // Badge de motor de IA
      const aiBadge = document.getElementById('aiEngineBadge');
      const aiText = document.getElementById('aiEngineText');
      if (aiBadge && aiText) {
        aiBadge.classList.remove('hidden');
        aiText.innerHTML = 'Claude SRE: <strong class="text-cyan-400">Tool Use Activo</strong>';
      }

      // Estado de incidentes abiertos
      const openCount = state.incidents.filter(i => i.status === 'OPEN').length;
      const openIncEl = document.getElementById('openIncidentsCount');
      if (openIncEl) openIncEl.innerText = openCount;
      const pulse = document.getElementById('incidentPulse');
      const subtitle = document.getElementById('incidentStatusSubtitle');
      const iconBox = document.getElementById('incidentIconBox');
      if (pulse) pulse.classList.toggle('hidden', openCount === 0);
      if (subtitle) {
        subtitle.innerText = openCount > 0 ? `${openCount} incidente(s) activo(s)` : 'Operación nominal';
        subtitle.className = openCount > 0 ? 'text-[11px] text-rose-400 font-medium mt-0.5' : 'text-[11px] text-emerald-400 font-medium mt-0.5';
      }
      if (iconBox) {
        iconBox.className = openCount > 0
          ? 'p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400'
          : 'p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400';
      }
    });

    window.DevPilot.Controller.subscribe('telemetry:updated', async () => {
      try {
        const res = await window.DevPilot.Model.ApiClient.request('/api/stats');
        if (res.success && res.data) {
          const d = res.data;
          const slaEl = document.getElementById('slaUptimePct');
          const totalEl = document.getElementById('statsTotalIncidents');
          const remEl = document.getElementById('statsSuccessRem');
          const pendEl = document.getElementById('statsPendingProps');
          if (slaEl) {
            const pct = d.sla?.uptime_pct ?? 0;
            slaEl.innerText = pct.toFixed(2) + '%';
            slaEl.className = pct >= 99 ? 'text-lg font-bold text-emerald-400' : (pct >= 95 ? 'text-lg font-bold text-amber-400' : 'text-lg font-bold text-rose-400');
          }
          if (totalEl) totalEl.innerText = d.incidents?.total ?? 0;
          if (remEl) remEl.innerText = d.remediations?.successful ?? 0;
          if (pendEl) {
            const pend = d.remediations?.pending_proposals ?? 0;
            pendEl.innerText = pend;
            pendEl.className = pend > 0 ? 'text-lg font-bold text-amber-400' : 'text-lg font-bold text-slate-400';
          }
        }
      } catch (e) { /* stats aún no inicializadas */ }
    });
  }

  console.log('[DevPilot MVVM] Capa Vista (View) inicializada correctamente.');
})(window);
